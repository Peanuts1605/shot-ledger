import sys
from types import SimpleNamespace

import pytest
from genblaze_core import StorageError

from shot_ledger import preflight_real_proof


def _set_required_env(monkeypatch):
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("B2_KEY_ID", "test-key")
    monkeypatch.setenv("B2_APP_KEY", "test-secret")
    monkeypatch.setenv("B2_BUCKET", "test-bucket")


def test_provider_preflight_retrieves_configured_model(monkeypatch):
    calls = []

    class FakeModels:
        def retrieve(self, model):
            calls.append(model)
            return SimpleNamespace(id=model)

    monkeypatch.setattr(
        "openai.OpenAI",
        lambda: SimpleNamespace(models=FakeModels()),
    )
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "openai")

    result = preflight_real_proof.verify_provider()

    assert calls == ["gpt-image-2"]
    assert result == {
        "provider": "openai",
        "model": "gpt-image-2",
        "status": "verified",
    }


def test_preflight_receipt_never_claims_generation(monkeypatch):
    _set_required_env(monkeypatch)
    monkeypatch.setattr(
        preflight_real_proof,
        "verify_provider",
        lambda: {"provider": "openai", "model": "gpt-image-2", "status": "verified"},
    )
    monkeypatch.setattr(
        preflight_real_proof,
        "verify_b2",
        lambda: {"bucket": "test-bucket", "region": "test-region", "status": "verified"},
    )

    receipt = preflight_real_proof.run()

    assert receipt["paid_generation_started"] is False
    assert receipt["planned_takes"] == 3
    assert receipt["status"] == "ready_for_spend_approval"


def test_b2_preflight_reports_configured_bucket_and_closes(monkeypatch):
    closed = []

    class FakeBackend:
        def close(self):
            closed.append(True)

    class FakeStorageBackend:
        @staticmethod
        def for_backblaze(*, preflight):
            assert preflight is True
            return FakeBackend()

    monkeypatch.setitem(
        sys.modules,
        "genblaze_s3",
        SimpleNamespace(S3StorageBackend=FakeStorageBackend),
    )
    monkeypatch.setenv("B2_BUCKET", "test-bucket")
    monkeypatch.setenv("B2_REGION", "us-east-005")

    result = preflight_real_proof.verify_b2()

    assert result == {
        "bucket": "test-bucket",
        "region": "us-east-005",
        "status": "verified",
    }
    assert closed == [True]


def test_b2_preflight_names_required_s3_key_capability(monkeypatch):
    class FakeStorageBackend:
        @staticmethod
        def for_backblaze(*, preflight):
            assert preflight is True
            raise StorageError("HeadBucket returned AccessDenied")

    monkeypatch.setitem(
        sys.modules,
        "genblaze_s3",
        SimpleNamespace(S3StorageBackend=FakeStorageBackend),
    )

    with pytest.raises(RuntimeError, match="List all bucket names") as captured:
        preflight_real_proof.verify_b2()

    assert isinstance(captured.value.__cause__, StorageError)
    assert "shot-ledger/" in str(captured.value)
