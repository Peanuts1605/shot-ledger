from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .b2_store import GenerationStore
from .decision import DecisionPacket, verify_packet
from .generation_state import GenerationState, generation_state_from_dict
from .repository import ReviewRepository, repository_from_env
from .review import revise_decision
from .verification import verify_scene

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parent / "web"
PROOF_ROOT = PROJECT_ROOT / "proof" / "local"
PACKET_PATH = PROOF_ROOT / "decision.json"
REAL_PROOF_ROOT = PROJECT_ROOT / "proof" / "real"

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
}


def scene_payload(
    packet: DecisionPacket,
    repository: ReviewRepository,
    *,
    write_enabled: bool = True,
) -> dict[str, Any]:
    payload = packet.to_dict()
    takes_by_id = {take.take_id: take for take in packet.takes}
    for take_payload in payload["takes"]:
        take = takes_by_id[take_payload["take_id"]]
        take_payload["preview_url"] = repository.preview_url(take)
    payload["integrity"] = "hash matches" if verify_packet(packet) else "hash mismatch"
    payload["media_integrity"] = verify_scene(repository, packet).to_dict()
    payload["storage_mode"] = repository.storage_mode
    payload["proof_scope"] = (
        "Synthetic local demonstration - not Genblaze or B2 provider evidence"
        if repository.storage_mode == "local proof"
        else "Live provider evidence reloaded from Backblaze B2"
    )
    payload["write_enabled"] = write_enabled
    return payload


def generation_payload(state: GenerationState, storage_mode: str) -> dict[str, Any]:
    payload = state.to_dict()
    payload.update(
        {
            "complete": state.complete,
            "pending_take_ids": list(state.pending_take_ids),
            "succeeded_count": len(state.successful_takes),
            "storage_mode": storage_mode,
            "retry_command": "python -m shot_ledger.retry_real_proof",
        }
    )
    return payload


def generation_state_from_env() -> tuple[GenerationState, str]:
    mode = os.environ.get("SHOT_LEDGER_STORAGE_MODE", "local").strip().lower()
    if mode == "b2":
        scene_id = os.environ.get("SHOT_LEDGER_SCENE_ID", "").strip()
        if not scene_id:
            raise RuntimeError("SHOT_LEDGER_SCENE_ID is required in B2 mode")
        return GenerationStore.from_backblaze_env().load(scene_id), "Backblaze B2"
    path = Path(
        os.environ.get(
            "SHOT_LEDGER_GENERATION_STATE_PATH",
            REAL_PROOF_ROOT / "generation-state.json",
        )
    )
    return generation_state_from_dict(json.loads(path.read_text(encoding="utf-8"))), "local proof"


class ShotLedgerServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        repository: ReviewRepository,
        write_enabled: bool,
    ) -> None:
        self.repository = repository
        self.write_enabled = write_enabled
        super().__init__(server_address, ShotLedgerHandler)


class ShotLedgerHandler(BaseHTTPRequestHandler):
    server_version = "ShotLedger/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    @property
    def repository(self) -> ReviewRepository:
        server = self.server
        if not isinstance(server, ShotLedgerServer):
            raise RuntimeError("Shot Ledger server repository is unavailable")
        return server.repository

    @property
    def write_enabled(self) -> bool:
        server = self.server
        if not isinstance(server, ShotLedgerServer):
            return False
        return server.write_enabled

    def _send_bytes(self, body: bytes, content_type: str, status: int = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        self._send_bytes(body, CONTENT_TYPES[".json"], status)

    def _serve_file(self, path: Path, root: Path) -> None:
        try:
            safe_path = path.resolve()
            safe_path.relative_to(root.resolve())
        except ValueError:
            self._send_json({"error": "invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        if not safe_path.is_file():
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        content_type = CONTENT_TYPES.get(safe_path.suffix, "application/octet-stream")
        self._send_bytes(safe_path.read_bytes(), content_type)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/healthz":
            self._send_json(
                {
                    "status": "ok",
                    "storage_mode": self.repository.storage_mode,
                    "write_enabled": self.write_enabled,
                }
            )
            return
        if path == "/api/scene":
            try:
                self._send_json(
                    scene_payload(
                        self.repository.load(),
                        self.repository,
                        write_enabled=self.write_enabled,
                    )
                )
            except (FileNotFoundError, RuntimeError, ValueError) as error:
                self._send_json({"error": str(error)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        if path == "/api/run-state":
            try:
                state, storage_mode = generation_state_from_env()
                self._send_json(generation_payload(state, storage_mode))
            except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
                self._send_json({"error": str(error)}, HTTPStatus.NOT_FOUND)
            return
        if path == "/api/export":
            try:
                self._send_json(self.repository.load().to_dict())
            except (FileNotFoundError, RuntimeError, ValueError) as error:
                self._send_json({"error": str(error)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        if path.startswith("/api/assets/"):
            take_id = path.removeprefix("/api/assets/")
            try:
                packet = self.repository.load()
                take = next(take for take in packet.takes if take.take_id == take_id)
                self._send_bytes(self.repository.read_asset(take), "image/png")
            except (FileNotFoundError, RuntimeError, StopIteration, ValueError) as error:
                self._send_json({"error": str(error)}, HTTPStatus.NOT_FOUND)
            return
        if path.startswith("/proof/"):
            self._serve_file(PROOF_ROOT / path.removeprefix("/proof/"), PROOF_ROOT)
            return
        if path == "/":
            path = "/index.html"
        self._serve_file(WEB_ROOT / path.removeprefix("/"), WEB_ROOT)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/decision":
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        if not self.write_enabled:
            self._send_json(
                {"error": "public B2 proof is read-only"},
                HTTPStatus.FORBIDDEN,
            )
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 2 or content_length > 16_384:
                raise ValueError("invalid request size")
            request = json.loads(self.rfile.read(content_length))
            packet = self.repository.load()
            revised = revise_decision(
                packet,
                keeper_take_id=str(request.get("keeper_take_id", "")),
                selection_reason=str(request.get("selection_reason", "")),
            )
            self.repository.save(revised)
        except (
            FileNotFoundError,
            KeyError,
            RuntimeError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(scene_payload(revised, self.repository, write_enabled=True))


def main() -> None:
    host = os.environ.get("SHOT_LEDGER_HOST", "127.0.0.1")
    port = int(os.environ.get("SHOT_LEDGER_PORT", os.environ.get("PORT", "4173")))
    mode = os.environ.get("SHOT_LEDGER_STORAGE_MODE", "local").strip().lower()
    if mode == "local" and not PACKET_PATH.exists():
        raise RuntimeError("run python -m shot_ledger.proof_local before starting the app")
    repository = repository_from_env(PACKET_PATH, PROOF_ROOT)
    write_enabled = mode == "local" or os.environ.get("SHOT_LEDGER_ALLOW_B2_WRITES") == "true"
    server = ShotLedgerServer((host, port), repository, write_enabled)
    print(f"Shot Ledger: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
