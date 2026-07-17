from __future__ import annotations

from dataclasses import replace

import pytest

from shot_ledger.decision import (
    Take,
    build_decision_packet,
    decision_packet_from_dict,
    verify_packet,
)


def make_take(take_id: str, changed_value: str) -> Take:
    digest = (take_id.encode("utf-8").hex() * 64)[:64]
    return Take(
        take_id=take_id,
        changed_variable="light_direction",
        changed_value=changed_value,
        prompt=f"Travel mug with {changed_value}",
        provider="proof",
        model="proof-v1",
        parameters={"size": "800x1000", "changed_value": changed_value},
        asset_uri=f"file:///{take_id}.png",
        asset_sha256=digest,
        manifest_hash=digest,
        manifest_uri=f"file:///{take_id}.manifest.json",
    )


def make_packet():
    return build_decision_packet(
        scene_id="scene-001",
        brief="Travel mug product shot",
        locked_variables={"frame": "4:5"},
        takes=[
            make_take("a", "window"),
            make_take("b", "overhead"),
            make_take("c", "side"),
        ],
        keeper_take_id="a",
        selection_reason="The handle remains readable.",
        created_at="2026-07-17T12:00:00+00:00",
    )


def test_packet_preserves_keeper_and_rejected_siblings():
    packet = make_packet()
    statuses = {take["take_id"]: take["status"] for take in packet.to_dict()["takes"]}

    assert statuses == {"a": "keeper", "b": "rejected", "c": "rejected"}
    assert verify_packet(packet)


def test_packet_requires_exactly_three_takes():
    with pytest.raises(ValueError, match="exactly three"):
        build_decision_packet(
            scene_id="scene-001",
            brief="Travel mug product shot",
            locked_variables={},
            takes=[make_take("a", "window")],
            keeper_take_id="a",
            selection_reason="Readable handle.",
        )


def test_packet_requires_one_controlled_variable():
    third = replace(make_take("c", "side"), changed_variable="camera_angle")
    with pytest.raises(ValueError, match="same changed variable"):
        build_decision_packet(
            scene_id="scene-001",
            brief="Travel mug product shot",
            locked_variables={},
            takes=[make_take("a", "window"), make_take("b", "overhead"), third],
            keeper_take_id="a",
            selection_reason="Readable handle.",
        )


def test_packet_detects_tampering():
    packet = make_packet()
    tampered = replace(packet, selection_reason="A different reason.")

    assert not verify_packet(tampered)


def test_stored_status_must_match_keeper():
    payload = make_packet().to_dict()
    payload["takes"][0]["status"] = "rejected"

    with pytest.raises(ValueError, match="status conflicts"):
        decision_packet_from_dict(payload)
