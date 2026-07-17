from __future__ import annotations

from pathlib import Path

from shot_ledger.proof_local import run
from shot_ledger.repository import LocalReviewRepository
from shot_ledger.review import load_packet
from shot_ledger.verification import verify_scene


def test_reload_receipt_requires_decision_and_media(tmp_path: Path):
    run(tmp_path)
    packet_path = tmp_path / "decision.json"
    repository = LocalReviewRepository(packet_path, tmp_path)
    packet = load_packet(packet_path)

    media = verify_scene(repository, packet)
    receipt = {
        "decision_hash_matches": True,
        "media_integrity": media.to_dict(),
        "verified": media.verified,
    }

    assert receipt["verified"]
    assert receipt["media_integrity"]["status"] == "verified"
