from __future__ import annotations

import json
import os
from pathlib import Path

from .decision import verify_packet
from .repository import B2ReviewRepository
from .verification import verify_scene


def build_receipt(repository: B2ReviewRepository) -> dict[str, object]:
    packet = repository.load()
    decision_hash_matches = verify_packet(packet)
    media = verify_scene(repository, packet)
    return {
        "scene_id": packet.scene_id,
        "packet_hash": packet.packet_hash,
        "decision_hash_matches": decision_hash_matches,
        "media_integrity": media.to_dict(),
        "verified": decision_hash_matches and media.verified,
    }


def main() -> None:
    repository = B2ReviewRepository.from_env()
    receipt = build_receipt(repository)
    output_dir = Path(
        os.environ.get(
            "SHOT_LEDGER_PROOF_DIR",
            Path(__file__).resolve().parents[2] / "proof" / "real",
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "b2-reload-verification.json"
    output_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not receipt["verified"]:
        raise RuntimeError(f"B2 reload verification failed; see {output_path}")
    print(f"Fresh-process B2 verification: {output_path}")


if __name__ == "__main__":
    main()
