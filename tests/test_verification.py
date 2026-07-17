from __future__ import annotations

from pathlib import Path

from shot_ledger.proof_local import run
from shot_ledger.repository import LocalReviewRepository
from shot_ledger.review import load_packet
from shot_ledger.verification import verify_scene


def _local_proof(tmp_path: Path):
    run(tmp_path)
    packet_path = tmp_path / "decision.json"
    return LocalReviewRepository(packet_path, tmp_path), load_packet(packet_path)


def test_local_proof_verifies_asset_bytes_manifest_and_provenance(tmp_path):
    repository, packet = _local_proof(tmp_path)

    result = verify_scene(repository, packet)

    assert result.verified
    assert len(result.takes) == 3
    assert all(take.asset_hash_matches for take in result.takes)
    assert all(take.manifest_hash_matches for take in result.takes)
    assert all(take.manifest_valid for take in result.takes)
    assert all(take.provenance_matches for take in result.takes)


def test_modified_asset_bytes_fail_verification(tmp_path):
    repository, packet = _local_proof(tmp_path)
    (tmp_path / "take-b.png").write_bytes(b"tampered")

    result = verify_scene(repository, packet)

    assert not result.verified
    take_b = next(take for take in result.takes if take.take_id == "take-b")
    assert not take_b.asset_hash_matches
    assert take_b.manifest_hash_matches
    assert take_b.manifest_valid
    assert take_b.provenance_matches
