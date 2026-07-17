from __future__ import annotations

from dataclasses import replace

from test_b2_store import make_packet

from shot_ledger.generation_state import (
    GenerationSlot,
    build_generation_state,
    humanize_generation_failure,
    verify_generation_state,
)


def test_generation_state_hash_rejects_status_tampering():
    packet = make_packet()
    state = build_generation_state(
        scene_id=packet.scene_id,
        brief=packet.brief,
        locked_variables=packet.locked_variables,
        changed_variable="light_direction",
        slots=[
            GenerationSlot("a", "window", "succeeded", 1, take=packet.takes[0]),
            GenerationSlot("b", "overhead", "pending", 0),
            GenerationSlot("c", "side", "pending", 0),
        ],
        updated_at="2026-07-17T12:00:00+00:00",
    )

    assert verify_generation_state(state)
    assert not verify_generation_state(replace(state, updated_at="tampered"))


def test_moderation_failure_copy_blames_filter_and_teaches_retry():
    label = humanize_generation_failure("nsfw", None)

    assert "provider filter" in label
    assert "Rephrase" in label
    assert "person" not in label
