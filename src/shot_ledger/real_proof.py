from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline, StepStatus
from genblaze_gmicloud import GMICloudImageProvider
from genblaze_s3 import S3StorageBackend

from .b2_store import DecisionStore, GenerationStore
from .decision import Take, build_decision_packet
from .generation_state import (
    GenerationSlot,
    GenerationState,
    build_generation_state,
    humanize_generation_failure,
)
from .proof_local import BRIEF, LIGHTING_TAKES

SCENE_ID = "public-safe-travel-mug-001"
LOCKED_VARIABLES = {
    "subject": "unbranded stainless-steel travel mug",
    "frame": "4:5",
    "background": "clean tabletop",
    "camera": "eye-level product shot",
}
PROOF_DIR = Path(__file__).resolve().parents[2] / "proof" / "real"


def _required_env() -> None:
    missing = [
        name
        for name in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET", "GMI_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(f"missing required environment variables: {', '.join(missing)}")


def _initial_state() -> GenerationState:
    return build_generation_state(
        scene_id=SCENE_ID,
        brief=BRIEF,
        locked_variables=LOCKED_VARIABLES,
        changed_variable="light_direction",
        slots=[
            GenerationSlot(take_id, lighting, "pending", 0) for take_id, lighting in LIGHTING_TAKES
        ],
    )


def _generation_parameters() -> dict[str, object]:
    return {
        "size": "2304x2880",
        "output_format": "png",
        "max_images": 1,
        "watermark": False,
    }


def _failed_slot(slot: GenerationSlot, error_code: object, error: object) -> GenerationSlot:
    normalized_code = str(error_code) if error_code else None
    return GenerationSlot(
        take_id=slot.take_id,
        changed_value=slot.changed_value,
        status="failed",
        attempts=slot.attempts + 1,
        error_code=normalized_code,
        failure_reason=humanize_generation_failure(normalized_code, error),
    )


def _generate_pending(state: GenerationState, backend: S3StorageBackend) -> GenerationState:
    pending = [slot for slot in state.slots if slot.status != "succeeded"]
    if not pending:
        return state

    model = os.environ.get("SHOT_LEDGER_GMI_MODEL", "seedream-5.0-lite")
    parameters = _generation_parameters()
    prompts = [f"{BRIEF} Lighting: {slot.changed_value}." for slot in pending]
    storage = ObjectStorageSink(backend, key_strategy=KeyStrategy.HIERARCHICAL)
    results = (
        Pipeline("shot-ledger-controlled-lighting")
        .step(
            GMICloudImageProvider(),
            model=model,
            prompt="{prompt}",
            modality=Modality.IMAGE,
            **parameters,
        )
        .batch_run(
            prompts=prompts,
            sink=storage,
            fail_fast=False,
            raise_on_failure=False,
            timeout=180,
        )
    )

    replacements: dict[str, GenerationSlot] = {}
    for slot, prompt, result in zip(pending, prompts, results, strict=True):
        step = result.run.steps[-1]
        if step.status != StepStatus.SUCCEEDED or not step.assets:
            replacements[slot.take_id] = _failed_slot(slot, step.error_code, step.error)
            continue

        asset = step.assets[0]
        manifest = result.manifest
        if (
            not asset.url
            or not asset.sha256
            or not manifest.manifest_uri
            or not manifest.canonical_hash
        ):
            replacements[slot.take_id] = _failed_slot(
                slot,
                "durable_provenance_missing",
                "provider succeeded without a durable asset and manifest",
            )
            continue

        take = Take(
            take_id=slot.take_id,
            changed_variable=state.changed_variable,
            changed_value=slot.changed_value,
            prompt=prompt,
            provider=step.provider,
            model=step.model,
            parameters=parameters,
            asset_uri=asset.url,
            asset_sha256=asset.sha256,
            manifest_hash=manifest.canonical_hash,
            manifest_uri=manifest.manifest_uri,
        )
        replacements[slot.take_id] = GenerationSlot(
            take_id=slot.take_id,
            changed_value=slot.changed_value,
            status="succeeded",
            attempts=slot.attempts + 1,
            take=take,
        )

    return build_generation_state(
        scene_id=state.scene_id,
        brief=state.brief,
        locked_variables=state.locked_variables,
        changed_variable=state.changed_variable,
        slots=[replacements.get(slot.take_id, slot) for slot in state.slots],
    )


def _write_local_state(state: GenerationState) -> Path:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    path = PROOF_DIR / "generation-state.json"
    path.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _finalize(state: GenerationState, backend: S3StorageBackend) -> None:
    state_path = _write_local_state(state)
    if not state.complete:
        failed = ", ".join(state.pending_take_ids)
        raise RuntimeError(
            f"real proof remains partial ({failed}); preserved state: {state_path}; "
            "retry with python -m shot_ledger.retry_real_proof"
        )

    packet = build_decision_packet(
        scene_id=state.scene_id,
        brief=state.brief,
        locked_variables=state.locked_variables,
        takes=state.successful_takes,
        keeper_take_id="take-a",
        selection_reason=(
            "The left window light keeps the lid readable and separates the handle "
            "without changing the calm tabletop mood."
        ),
    )
    decision_key = DecisionStore(backend).save(packet)
    receipt = {
        "decision_key": decision_key,
        "generation_state_hash": state.state_hash,
        "packet_hash": packet.packet_hash,
        "scene_id": packet.scene_id,
        "take_attempts": {slot.take_id: slot.attempts for slot in state.slots},
        "take_manifest_hashes": {take.take_id: take.manifest_hash for take in packet.takes},
        "decision_stored": True,
    }
    receipt_path = PROOF_DIR / "real-proof-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"B2 decision key: {decision_key}")
    print(f"Packet hash: {packet.packet_hash}")
    print(f"Receipt: {receipt_path}")
    subprocess.run(
        [sys.executable, "-m", "shot_ledger.verify_b2"],
        check=True,
        env={**os.environ, "SHOT_LEDGER_SCENE_ID": packet.scene_id},
    )


def run(*, resume: bool = False) -> None:
    _required_env()
    backend = S3StorageBackend.for_backblaze()
    state_store = GenerationStore(backend)
    state = state_store.load(SCENE_ID) if resume else _initial_state()
    state_store.save(state)
    state = _generate_pending(state, backend)
    state_store.save(state)
    _finalize(state, backend)


if __name__ == "__main__":
    run()
