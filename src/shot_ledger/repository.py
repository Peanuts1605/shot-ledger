from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol
from urllib.parse import unquote, urlparse

from .b2_store import DecisionStore, ObjectBackend
from .decision import DecisionPacket, Take
from .review import load_packet, save_packet


class ReviewRepository(Protocol):
    storage_mode: str

    def load(self) -> DecisionPacket: ...

    def save(self, packet: DecisionPacket) -> None: ...

    def preview_url(self, take: Take) -> str: ...

    def read_asset(self, take: Take) -> bytes: ...

    def read_manifest(self, take: Take) -> bytes: ...


class LocalReviewRepository:
    storage_mode = "local proof"

    def __init__(self, packet_path: Path, proof_root: Path) -> None:
        self._packet_path = packet_path
        self._proof_root = proof_root

    def load(self) -> DecisionPacket:
        return load_packet(self._packet_path)

    def save(self, packet: DecisionPacket) -> None:
        save_packet(packet, self._proof_root)

    def preview_url(self, take: Take) -> str:
        return f"/proof/{take.take_id}.png"

    def read_asset(self, take: Take) -> bytes:
        return self._read_proof_uri(take.asset_uri)

    def read_manifest(self, take: Take) -> bytes:
        return self._read_proof_uri(take.manifest_uri)

    def _read_proof_uri(self, uri: str) -> bytes:
        parsed = urlparse(uri)
        if parsed.scheme == "synthetic" and parsed.netloc == "shot-ledger":
            filename = Path(unquote(parsed.path)).name
            if not filename:
                raise ValueError("synthetic proof URI must name an artifact")
            path = (self._proof_root / filename).resolve()
        elif parsed.scheme == "file" and parsed.netloc in {"", "localhost"}:
            path = Path(unquote(parsed.path)).resolve()
        else:
            raise ValueError("local proof URI must use the file or synthetic scheme")
        try:
            path.relative_to(self._proof_root.resolve())
        except ValueError as error:
            raise ValueError("local proof URI is outside the proof directory") from error
        return path.read_bytes()


class B2AssetBackend(ObjectBackend, Protocol):
    def key_from_url(self, url: str) -> str | None: ...


class B2ReviewRepository:
    storage_mode = "Backblaze B2"

    def __init__(self, backend: B2AssetBackend, scene_id: str) -> None:
        self._backend = backend
        self._scene_id = scene_id
        self._decisions = DecisionStore(backend)

    @classmethod
    def from_env(cls) -> B2ReviewRepository:
        from genblaze_s3 import S3StorageBackend

        scene_id = os.environ.get("SHOT_LEDGER_SCENE_ID", "").strip()
        if not scene_id:
            raise RuntimeError("SHOT_LEDGER_SCENE_ID is required in B2 mode")
        return cls(S3StorageBackend.for_backblaze(), scene_id)

    def load(self) -> DecisionPacket:
        return self._decisions.load(self._scene_id)

    def save(self, packet: DecisionPacket) -> None:
        if packet.scene_id != self._scene_id:
            raise ValueError("packet scene does not match the configured B2 scene")
        self._decisions.save(packet)

    def preview_url(self, take: Take) -> str:
        return f"/api/assets/{take.take_id}"

    def read_asset(self, take: Take) -> bytes:
        key = self._backend.key_from_url(take.asset_uri)
        if key is None:
            raise ValueError("asset URI does not belong to the configured B2 bucket")
        return self._backend.get(key)

    def read_manifest(self, take: Take) -> bytes:
        key = self._backend.key_from_url(take.manifest_uri)
        if key is None:
            raise ValueError("manifest URI does not belong to the configured B2 bucket")
        return self._backend.get(key)


def repository_from_env(packet_path: Path, proof_root: Path) -> ReviewRepository:
    mode = os.environ.get("SHOT_LEDGER_STORAGE_MODE", "local").strip().lower()
    if mode == "local":
        return LocalReviewRepository(packet_path, proof_root)
    if mode == "b2":
        return B2ReviewRepository.from_env()
    raise RuntimeError("SHOT_LEDGER_STORAGE_MODE must be local or b2")
