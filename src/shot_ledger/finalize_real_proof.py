from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .b2_store import DecisionStore, GenerationStore
from .finalize import build_reviewed_decision

DEFAULT_SCENE_ID = "public-safe-travel-mug-001"
PROOF_DIR = Path(__file__).resolve().parents[2] / "proof" / "real"


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seal a human-reviewed Shot Ledger keeper and verify it from B2."
    )
    parser.add_argument("--keeper", required=True, help="Take ID selected after visual review")
    parser.add_argument("--reason", required=True, help="Concrete visible reason the take won")
    return parser.parse_args()


def main() -> None:
    from genblaze_s3 import S3StorageBackend

    arguments = _arguments()
    scene_id = os.environ.get("SHOT_LEDGER_SCENE_ID", DEFAULT_SCENE_ID).strip()
    backend = S3StorageBackend.for_backblaze()
    state = GenerationStore(backend).load(scene_id)
    packet = build_reviewed_decision(
        state,
        keeper_take_id=arguments.keeper,
        selection_reason=arguments.reason,
    )
    decision_key = DecisionStore(backend).save(packet)

    receipt = {
        "decision_key": decision_key,
        "decision_stored": True,
        "generation_state_hash": state.state_hash,
        "human_review_required": True,
        "keeper_take_id": packet.keeper_take_id,
        "packet_hash": packet.packet_hash,
        "scene_id": packet.scene_id,
        "selection_reason": packet.selection_reason,
        "take_attempts": {slot.take_id: slot.attempts for slot in state.slots},
        "take_manifest_hashes": {take.take_id: take.manifest_hash for take in packet.takes},
    }
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = PROOF_DIR / "real-proof-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"B2 decision key: {decision_key}")
    print(f"Keeper: {packet.keeper_take_id}")
    print(f"Packet hash: {packet.packet_hash}")
    subprocess.run(
        [sys.executable, "-m", "shot_ledger.verify_b2"],
        check=True,
        env={**os.environ, "SHOT_LEDGER_SCENE_ID": packet.scene_id},
    )
    verification_path = PROOF_DIR / "b2-reload-verification.json"
    verification_key = f"shot-ledger/scenes/{packet.scene_id}/verification.json"
    backend.put(
        verification_key,
        verification_path.read_bytes(),
        content_type="application/json",
        metadata={"packet-sha256": packet.packet_hash},
    )
    receipt["verification_key"] = verification_key
    receipt["verification_stored"] = True
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"B2 verification key: {verification_key}")
    print(f"Receipt: {receipt_path}")


if __name__ == "__main__":
    main()
