from __future__ import annotations

from dataclasses import replace

from test_decision import make_take

from shot_ledger.b2_store import DecisionStore, GenerationStore
from shot_ledger.decision import build_decision_packet
from shot_ledger.generation_state import GenerationSlot, build_generation_state


class MemoryBackend:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.metadata: dict[str, dict[str, str]] = {}

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        self.objects[key] = data
        self.metadata[key] = metadata or {}
        return key

    def get(self, key: str) -> bytes:
        return self.objects[key]


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


def test_fresh_store_reloads_complete_decision():
    backend = MemoryBackend()
    first_process = DecisionStore(backend)
    packet = make_packet()

    key = first_process.save(packet)
    second_process = DecisionStore(backend)
    reloaded = second_process.load(packet.scene_id)

    assert key == "shot-ledger/scenes/scene-001/decision.json"
    assert reloaded == packet
    assert backend.metadata[key]["packet-sha256"] == packet.packet_hash


def test_store_rejects_tampered_packet():
    backend = MemoryBackend()
    packet = replace(make_packet(), selection_reason="Changed after signing")

    try:
        DecisionStore(backend).save(packet)
    except ValueError as error:
        assert "invalid decision packet" in str(error)
    else:
        raise AssertionError("tampered packet was stored")


def test_generation_store_preserves_successes_and_failed_retry_slot():
    backend = MemoryBackend()
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
                error_code="timeout",
                failure_reason="Retry only this take.",
            ),
            GenerationSlot("c", "side", "succeeded", 1, take=packet.takes[2]),
        ],
        updated_at="2026-07-17T12:00:00+00:00",
    )

    key = GenerationStore(backend).save(state)
    reloaded = GenerationStore(backend).load(packet.scene_id)

    assert key == "shot-ledger/scenes/scene-001/generation-state.json"
    assert reloaded == state
    assert reloaded.pending_take_ids == ("b",)
    assert [take.take_id for take in reloaded.successful_takes] == ["a", "c"]
    assert backend.metadata[key]["state-sha256"] == state.state_hash
