from __future__ import annotations

import json
from typing import Protocol

from .decision import DecisionPacket, decision_packet_from_dict, verify_packet
from .generation_state import (
    GenerationState,
    generation_state_from_dict,
    verify_generation_state,
)


class ObjectBackend(Protocol):
    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str: ...

    def get(self, key: str) -> bytes: ...


class DecisionStore:
    def __init__(self, backend: ObjectBackend, prefix: str = "shot-ledger") -> None:
        self._backend = backend
        self._prefix = prefix.strip("/")

    @classmethod
    def from_backblaze_env(cls, prefix: str = "shot-ledger") -> DecisionStore:
        from genblaze_s3 import S3StorageBackend

        return cls(S3StorageBackend.for_backblaze(), prefix=prefix)

    def key_for(self, scene_id: str) -> str:
        clean_scene_id = scene_id.strip().replace("/", "-")
        if not clean_scene_id:
            raise ValueError("scene_id is required")
        return f"{self._prefix}/scenes/{clean_scene_id}/decision.json"

    def save(self, packet: DecisionPacket) -> str:
        if not verify_packet(packet):
            raise ValueError("refusing to store an invalid decision packet")
        key = self.key_for(packet.scene_id)
        payload = json.dumps(packet.to_dict(), sort_keys=True, indent=2).encode("utf-8")
        self._backend.put(
            key,
            payload,
            content_type="application/json",
            metadata={"packet-sha256": packet.packet_hash},
        )
        return key

    def load(self, scene_id: str) -> DecisionPacket:
        payload = json.loads(self._backend.get(self.key_for(scene_id)).decode("utf-8"))
        return decision_packet_from_dict(payload)


class GenerationStore:
    def __init__(self, backend: ObjectBackend, prefix: str = "shot-ledger") -> None:
        self._backend = backend
        self._prefix = prefix.strip("/")

    @classmethod
    def from_backblaze_env(cls, prefix: str = "shot-ledger") -> GenerationStore:
        from genblaze_s3 import S3StorageBackend

        return cls(S3StorageBackend.for_backblaze(), prefix=prefix)

    def key_for(self, scene_id: str) -> str:
        clean_scene_id = scene_id.strip().replace("/", "-")
        if not clean_scene_id:
            raise ValueError("scene_id is required")
        return f"{self._prefix}/scenes/{clean_scene_id}/generation-state.json"

    def save(self, state: GenerationState) -> str:
        if not verify_generation_state(state):
            raise ValueError("refusing to store invalid generation state")
        key = self.key_for(state.scene_id)
        payload = json.dumps(state.to_dict(), sort_keys=True, indent=2).encode("utf-8")
        self._backend.put(
            key,
            payload,
            content_type="application/json",
            metadata={"state-sha256": state.state_hash},
        )
        return key

    def load(self, scene_id: str) -> GenerationState:
        payload = json.loads(self._backend.get(self.key_for(scene_id)).decode("utf-8"))
        return generation_state_from_dict(payload)
