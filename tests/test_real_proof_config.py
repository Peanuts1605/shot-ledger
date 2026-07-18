import pytest
from genblaze_s3 import S3StorageBackend

from shot_ledger import real_proof
from shot_ledger.real_proof import _provider_name, _provider_settings, _required_env


def _set_b2(monkeypatch):
    monkeypatch.setenv("B2_KEY_ID", "test-key")
    monkeypatch.setenv("B2_APP_KEY", "test-secret")
    monkeypatch.setenv("B2_BUCKET", "test-bucket")


def test_openai_is_default_with_exact_four_by_five_output(monkeypatch):
    monkeypatch.delenv("SHOT_LEDGER_PROVIDER", raising=False)
    monkeypatch.delenv("SHOT_LEDGER_OPENAI_MODEL", raising=False)

    model, parameters = _provider_settings()

    assert _provider_name() == "openai"
    assert model == "gpt-image-2"
    assert parameters == {
        "size": "1024x1280",
        "quality": "medium",
        "output_format": "png",
        "n": 1,
    }


def test_gmi_route_keeps_existing_provider_contract(monkeypatch):
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "gmi")
    monkeypatch.delenv("SHOT_LEDGER_GMI_MODEL", raising=False)

    model, parameters = _provider_settings()

    assert model == "seedream-5.0-lite"
    assert parameters["size"] == "2304x2880"
    assert parameters["max_images"] == 1


def test_required_env_only_demands_selected_provider_key(monkeypatch):
    _set_b2(monkeypatch)
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.delenv("GMI_API_KEY", raising=False)

    _required_env()


def test_required_env_names_missing_selected_provider_key(monkeypatch):
    _set_b2(monkeypatch)
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "gmi")
    monkeypatch.delenv("GMI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GMI_API_KEY"):
        _required_env()


def test_unknown_provider_fails_before_generation(monkeypatch):
    monkeypatch.setenv("SHOT_LEDGER_PROVIDER", "mystery")

    with pytest.raises(RuntimeError, match="unsupported SHOT_LEDGER_PROVIDER"):
        _provider_name()


def test_genblaze_storage_stays_inside_shot_ledger_prefix(monkeypatch):
    options = {}
    backend = object()

    monkeypatch.setattr(S3StorageBackend, "for_backblaze", lambda: backend)

    def fake_sink(received_backend, **kwargs):
        assert received_backend is backend
        options.update(kwargs)
        return object()

    monkeypatch.setattr(real_proof, "ObjectStorageSink", fake_sink)

    real_proof._generation_storage_sink()

    assert options["prefix"] == "shot-ledger/genblaze"
