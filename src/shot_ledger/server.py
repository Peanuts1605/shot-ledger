from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .decision import DecisionPacket, verify_packet
from .review import load_packet, revise_decision, save_packet

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parent / "web"
PROOF_ROOT = PROJECT_ROOT / "proof" / "local"
PACKET_PATH = PROOF_ROOT / "decision.json"

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
}


def scene_payload(packet: DecisionPacket) -> dict[str, Any]:
    payload = packet.to_dict()
    for take in payload["takes"]:
        take["preview_url"] = f"/proof/{take['take_id']}.png"
    payload["integrity"] = "verified" if verify_packet(packet) else "failed"
    payload["storage_mode"] = "local proof"
    return payload


class ShotLedgerHandler(BaseHTTPRequestHandler):
    server_version = "ShotLedger/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

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
        if path == "/api/scene":
            if not PACKET_PATH.exists():
                self._send_json(
                    {"error": "run python -m shot_ledger.proof_local first"},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
                return
            self._send_json(scene_payload(load_packet(PACKET_PATH)))
            return
        if path == "/api/export":
            self._serve_file(PACKET_PATH, PROOF_ROOT)
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
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 2 or content_length > 16_384:
                raise ValueError("invalid request size")
            request = json.loads(self.rfile.read(content_length))
            packet = load_packet(PACKET_PATH)
            revised = revise_decision(
                packet,
                keeper_take_id=str(request.get("keeper_take_id", "")),
                selection_reason=str(request.get("selection_reason", "")),
            )
            save_packet(revised, PROOF_ROOT)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(scene_payload(revised))


def main() -> None:
    host = os.environ.get("SHOT_LEDGER_HOST", "127.0.0.1")
    port = int(os.environ.get("SHOT_LEDGER_PORT", "4173"))
    if not PACKET_PATH.exists():
        raise RuntimeError("run python -m shot_ledger.proof_local before starting the app")
    server = ThreadingHTTPServer((host, port), ShotLedgerHandler)
    print(f"Shot Ledger: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
