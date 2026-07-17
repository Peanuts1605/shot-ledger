from __future__ import annotations

from dataclasses import replace

from test_decision import make_take

from shot_ledger.b2_store import DecisionStore
from shot_ledger.decision import build_decision_packet


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
