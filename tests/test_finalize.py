from __future__ import annotations

import pytest
from test_b2_store import MemoryBackend, make_packet

from shot_ledger.finalize import build_reviewed_decision
from shot_ledger.finalize_real_proof import publish_verification_receipt
from shot_ledger.generation_state import GenerationSlot, build_generation_state


def _state(*, complete: bool):
    packet = make_packet()
    return build_generation_state(
        scene_id=packet.scene_id,
        brief=packet.brief,
        locked_variables=packet.locked_variables,
        changed_variable="light_direction",
        slots=[
            GenerationSlot("a", "window", "succeeded", 1, take=packet.takes[0]),
            GenerationSlot("b", "overhead", "succeeded", 1, take=packet.takes[1]),
            (
                GenerationSlot("c", "side", "succeeded", 1, take=packet.takes[2])
                if complete
                else GenerationSlot("c", "side", "pending", 0)
            ),
        ],
        updated_at="2026-07-17T12:00:00+00:00",
    )


def test_build_reviewed_decision_uses_explicit_human_choice():
    packet = build_reviewed_decision(
        _state(complete=True),
        keeper_take_id="b",
        selection_reason="The overhead take keeps the rim and handle equally readable.",
    )

    assert packet.keeper_take_id == "b"
    assert packet.selection_reason == "The overhead take keeps the rim and handle equally readable."


def test_build_reviewed_decision_refuses_partial_generation():
    with pytest.raises(ValueError, match="all three takes"):
        build_reviewed_decision(
            _state(complete=False),
            keeper_take_id="a",
            selection_reason="The handle remains readable.",
        )


def test_publish_verification_receipt_requires_matching_verified_packet(tmp_path):
    backend = MemoryBackend()
    path = tmp_path / "verification.json"
    path.write_text(
        '{"packet_hash":"packet-123","verified":true}\n',
        encoding="utf-8",
    )

    key = publish_verification_receipt(
        backend,
        scene_id="scene-001",
        packet_hash="packet-123",
        verification_path=path,
    )

    assert key == "shot-ledger/scenes/scene-001/verification.json"
    assert backend.objects[key] == path.read_bytes()
    assert backend.metadata[key]["packet-sha256"] == "packet-123"


def test_publish_verification_receipt_rejects_stale_packet(tmp_path):
    path = tmp_path / "verification.json"
    path.write_text(
        '{"packet_hash":"old-packet","verified":true}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match"):
        publish_verification_receipt(
            MemoryBackend(),
            scene_id="scene-001",
            packet_hash="new-packet",
            verification_path=path,
        )
