from __future__ import annotations

import json
import os
from pathlib import Path

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline, StepStatus
from genblaze_gmicloud import GMICloudImageProvider
from genblaze_s3 import S3StorageBackend

from .b2_store import DecisionStore
from .decision import Take, build_decision_packet, verify_packet
from .proof_local import BRIEF

LIGHTING = (
    ("take-a", "left window light"),
    ("take-b", "overhead softbox"),
    ("take-c", "low side light"),
)


def _required_env() -> None:
    missing = [
        name
        for name in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET", "GMI_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(f"missing required environment variables: {', '.join(missing)}")


def run() -> None:
    _required_env()
    model = os.environ.get("SHOT_LEDGER_GMI_MODEL", "seedream-5.0-lite")
    prompts = [f"{BRIEF} Lighting: {lighting}." for _, lighting in LIGHTING]

    storage = ObjectStorageSink(
        S3StorageBackend.for_backblaze(),
        key_strategy=KeyStrategy.HIERARCHICAL,
    )
    results = (
        Pipeline("shot-ledger-controlled-lighting")
        .step(
            GMICloudImageProvider(),
            model=model,
            prompt="{prompt}",
            modality=Modality.IMAGE,
            aspect_ratio="4:5",
        )
        .batch_run(
            prompts=prompts,
            sink=storage,
            fail_fast=False,
            raise_on_failure=False,
            timeout=180,
        )
    )

    partial = []
    takes: list[Take] = []
    for (take_id, lighting), prompt, result in zip(LIGHTING, prompts, results, strict=True):
        step = result.run.steps[-1]
        if step.status != StepStatus.SUCCEEDED or not step.assets:
            partial.append(
                {
                    "take_id": take_id,
                    "status": str(step.status),
                    "error_code": step.error_code,
                    "error": step.error,
                }
            )
            continue

        asset = step.assets[0]
        if not asset.sha256 or not result.manifest.manifest_uri:
            raise RuntimeError(f"{take_id} did not receive durable asset provenance")
        takes.append(
            Take(
                take_id=take_id,
                changed_variable="light_direction",
                changed_value=lighting,
                prompt=prompt,
                provider=step.provider,
                model=step.model,
                asset_uri=asset.url,
                asset_sha256=asset.sha256,
                manifest_hash=result.manifest.canonical_hash,
                manifest_uri=result.manifest.manifest_uri,
            )
        )

    proof_dir = Path(__file__).resolve().parents[2] / "proof" / "real"
    proof_dir.mkdir(parents=True, exist_ok=True)
    if partial or len(takes) != 3:
        (proof_dir / "partial-generation.json").write_text(
            json.dumps(partial, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError("real proof is partial; failed takes were preserved")

    packet = build_decision_packet(
        scene_id="public-safe-travel-mug-001",
        brief=BRIEF,
        locked_variables={
            "subject": "unbranded stainless-steel travel mug",
            "frame": "4:5",
            "background": "clean tabletop",
            "camera": "eye-level product shot",
        },
        takes=takes,
        keeper_take_id="take-a",
        selection_reason=(
            "The left window light keeps the lid readable and separates the handle "
            "without changing the calm tabletop mood."
        ),
    )

    first_store = DecisionStore.from_backblaze_env()
    decision_key = first_store.save(packet)

    fresh_store = DecisionStore.from_backblaze_env()
    reloaded = fresh_store.load(packet.scene_id)
    if not verify_packet(reloaded) or reloaded.packet_hash != packet.packet_hash:
        raise RuntimeError("fresh B2 reload did not reproduce the decision packet")

    receipt = {
        "decision_key": decision_key,
        "packet_hash": packet.packet_hash,
        "scene_id": packet.scene_id,
        "take_manifest_hashes": {take.take_id: take.manifest_hash for take in packet.takes},
        "verified": True,
    }
    receipt_path = proof_dir / "real-proof-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"B2 decision key: {decision_key}")
    print(f"Packet hash: {packet.packet_hash}")
    print(f"Receipt: {receipt_path}")
    print("Fresh B2 reload verified: True")


if __name__ == "__main__":
    run()
