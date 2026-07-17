from __future__ import annotations

from test_b2_store import make_packet

from shot_ledger.review import revise_decision
from shot_ledger.server import scene_payload


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


def test_local_review_never_claims_b2_from_environment_alone(monkeypatch):
    monkeypatch.setenv("B2_BUCKET", "configured-but-not-loaded")

    payload = scene_payload(make_packet())

    assert payload["storage_mode"] == "local proof"
    assert payload["integrity"] == "verified"
