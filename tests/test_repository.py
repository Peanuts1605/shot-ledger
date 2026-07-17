from __future__ import annotations

from dataclasses import replace

from test_b2_store import MemoryBackend, make_packet

from shot_ledger.repository import B2ReviewRepository


class MemoryB2Backend(MemoryBackend):
    def get_durable_url(self, key: str) -> str:
        return f"https://s3.example.invalid/bucket/{key}"

    def key_from_url(self, url: str) -> str | None:
        prefix = "https://s3.example.invalid/bucket/"
        return url.removeprefix(prefix) if url.startswith(prefix) else None


def test_b2_repository_reloads_and_updates_decision():
    backend = MemoryB2Backend()
    original = make_packet()
    repository = B2ReviewRepository(backend, original.scene_id)

    repository.save(original)
    reloaded = repository.load()

    assert reloaded == original
    assert repository.storage_mode == "Backblaze B2"
    assert repository.preview_url(original.takes[0]) == "/api/assets/a"


def test_b2_repository_reads_private_asset_by_durable_url():
    backend = MemoryB2Backend()
    packet = make_packet()
    repository = B2ReviewRepository(backend, packet.scene_id)
    asset_key = "shot-ledger/assets/a.png"
    backend.objects[asset_key] = b"private-image"
    take = replace(packet.takes[0], asset_uri=backend.get_durable_url(asset_key))

    assert repository.read_asset(take) == b"private-image"


def test_b2_repository_reads_private_manifest_by_durable_url():
    backend = MemoryB2Backend()
    packet = make_packet()
    repository = B2ReviewRepository(backend, packet.scene_id)
    manifest_key = "shot-ledger/manifests/a.json"
    backend.objects[manifest_key] = b'{"manifest": "private"}'
    take = replace(packet.takes[0], manifest_uri=backend.get_durable_url(manifest_key))

    assert repository.read_manifest(take) == b'{"manifest": "private"}'


def test_b2_repository_rejects_foreign_asset_url():
    backend = MemoryB2Backend()
    packet = make_packet()
    repository = B2ReviewRepository(backend, packet.scene_id)

    try:
        repository.read_asset(packet.takes[0])
    except ValueError as error:
        assert "configured B2 bucket" in str(error)
    else:
        raise AssertionError("foreign asset URL was accepted")


def test_b2_repository_rejects_foreign_manifest_url():
    backend = MemoryB2Backend()
    packet = make_packet()
    repository = B2ReviewRepository(backend, packet.scene_id)

    try:
        repository.read_manifest(packet.takes[0])
    except ValueError as error:
        assert "configured B2 bucket" in str(error)
    else:
        raise AssertionError("foreign manifest URL was accepted")
