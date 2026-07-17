from __future__ import annotations

import json
import threading
from http.client import HTTPConnection

from test_b2_store import make_packet

from shot_ledger.generation_state import GenerationSlot, build_generation_state
from shot_ledger.repository import LocalReviewRepository
from shot_ledger.review import revise_decision, save_packet
from shot_ledger.server import ShotLedgerServer, generation_payload, scene_payload


def test_revise_decision_changes_keeper_reason_and_hash():
    original = make_packet()

    revised = revise_decision(
        original,
        keeper_take_id="b",
        selection_reason="The overhead light makes the lid mechanism easiest to inspect.",
    )

    assert revised.keeper_take_id == "b"
    assert revised.selection_reason.startswith("The overhead light")
    assert revised.packet_hash != original.packet_hash


def test_revise_decision_rejects_unknown_keeper():
    original = make_packet()

    try:
        revise_decision(
            original,
            keeper_take_id="missing",
            selection_reason="This should not save.",
        )
    except ValueError as error:
        assert "one of the three" in str(error)
    else:
        raise AssertionError("unknown keeper was accepted")


def test_local_review_never_claims_b2_from_environment_alone(monkeypatch, tmp_path):
    packet = make_packet()
    packet_path = save_packet(packet, tmp_path)
    repository = LocalReviewRepository(packet_path, tmp_path)
    monkeypatch.setenv("B2_BUCKET", "configured-but-not-loaded")

    payload = scene_payload(packet, repository)

    assert payload["storage_mode"] == "local proof"
    assert payload["integrity"] == "hash matches"
    assert payload["media_integrity"]["status"] == "not verified"
    assert payload["proof_scope"].startswith("Synthetic local demonstration")
    assert payload["write_enabled"]


def test_public_b2_payload_can_be_explicitly_read_only(tmp_path):
    packet = make_packet()
    packet_path = save_packet(packet, tmp_path)
    repository = LocalReviewRepository(packet_path, tmp_path)

    payload = scene_payload(packet, repository, write_enabled=False)

    assert not payload["write_enabled"]


def test_read_only_server_rejects_decision_write(tmp_path):
    packet = make_packet()
    packet_path = save_packet(packet, tmp_path)
    repository = LocalReviewRepository(packet_path, tmp_path)
    server = ShotLedgerServer(("127.0.0.1", 0), repository, write_enabled=False)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection(*server.server_address, timeout=2)
    try:
        connection.request(
            "POST",
            "/api/decision",
            body=json.dumps(
                {
                    "keeper_take_id": "b",
                    "selection_reason": "This must not overwrite the shared proof.",
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read())
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 403
    assert payload["error"] == "public B2 proof is read-only"
    assert repository.load() == packet


def test_partial_generation_payload_preserves_retry_truth():
    packet = make_packet()
    state = build_generation_state(
        scene_id=packet.scene_id,
        brief=packet.brief,
        locked_variables=packet.locked_variables,
        changed_variable="light_direction",
        slots=[
            GenerationSlot("a", "window", "succeeded", 1, take=packet.takes[0]),
            GenerationSlot(
                "b",
                "overhead",
                "failed",
                1,
                failure_reason="Retry only this take.",
            ),
            GenerationSlot("c", "side", "succeeded", 1, take=packet.takes[2]),
        ],
        updated_at="2026-07-17T12:00:00+00:00",
    )

    payload = generation_payload(state, "Backblaze B2")

    assert not payload["complete"]
    assert payload["succeeded_count"] == 2
    assert payload["pending_take_ids"] == ["b"]
    assert payload["retry_command"] == "python -m shot_ledger.retry_real_proof"
