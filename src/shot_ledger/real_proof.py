from __future__ import annotations

import json
import os
from pathlib import Path

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline, StepStatus
from genblaze_gmicloud import GMICloudImageProvider
from genblaze_s3 import S3StorageBackend

from .b2_store import GenerationStore
from .decision import Take
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


def _write_review_assets(state: GenerationState, backend: S3StorageBackend) -> list[Path]:
    review_dir = PROOF_DIR / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for take in state.successful_takes:
        key = backend.key_from_url(take.asset_uri)
        if key is None:
            raise RuntimeError(f"{take.take_id} asset is outside the configured B2 bucket")
        path = review_dir / f"{take.take_id}.png"
        path.write_bytes(backend.get(key))
        paths.append(path)
    return paths


def _finish_generation(state: GenerationState, backend: S3StorageBackend) -> None:
    state_path = _write_local_state(state)
    if not state.complete:
        failed = ", ".join(state.pending_take_ids)
        raise RuntimeError(
            f"real proof remains partial ({failed}); preserved state: {state_path}; "
            "retry with python -m shot_ledger.retry_real_proof"
        )
    review_paths = _write_review_assets(state, backend)
    print(f"Generation state: {state_path}")
    for path in review_paths:
        print(f"Review take: {path}")
    print("No keeper has been selected yet.")
    print(
        "After reviewing all three images, seal one with: "
        "python -m shot_ledger.finalize_real_proof --keeper <take-id> --reason <visible-reason>"
    )


def run(*, resume: bool = False) -> None:
    _required_env()
    backend = S3StorageBackend.for_backblaze()
    state_store = GenerationStore(backend)
    state = state_store.load(SCENE_ID) if resume else _initial_state()
    state_store.save(state)
    state = _generate_pending(state, backend)
    state_store.save(state)
    _finish_generation(state, backend)


if __name__ == "__main__":
    run()
