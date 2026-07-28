import hashlib

import pytest

from contracts.common.envelope import ArtifactRefV1
from orchestrator.storage import get_artifact, put_artifact


def test_put_and_get_artifact_round_trip(tmp_path):
    payload = b"hello artifact storage"
    ref = put_artifact(payload, artifact_id="artifact_001", mime_type="text/plain")

    assert ref.artifact_id == "artifact_001"
    assert ref.hash == hashlib.sha256(payload).hexdigest()
    assert ref.path.startswith("s3://")
    assert ref.mime_type == "text/plain"
    assert isinstance(ref.created_at, object)

    fetched = get_artifact(ref)
    assert fetched == payload


def test_get_artifact_detects_corrupted_object(monkeypatch):
    payload = b"good data"
    ref = put_artifact(payload, artifact_id="artifact_002", mime_type="text/plain")

    from orchestrator.storage import _bucket_and_key_from_path, _make_s3_client

    bucket, key = _bucket_and_key_from_path(ref.path)
    client = _make_s3_client()
    client.put_object(Bucket=bucket, Key=key, Body=b"corrupted data", ContentType="text/plain")

    with pytest.raises(ValueError, match="Stored artifact hash mismatch"):
        get_artifact(ref)
