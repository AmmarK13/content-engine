from datetime import datetime, timezone,UTC

import pytest
from pydantic import ValidationError

from contracts.common.manifest import (
    ArtifactRefV1,
    ProductionManifestV1,
    StageRecordV1,
    StageStatus,
)


class TestStageStatus:
    def test_values(self):
        assert StageStatus.PENDING == "pending"
        assert StageStatus.RUNNING == "running"
        assert StageStatus.PASSED == "passed"
        assert StageStatus.FAILED == "failed"


class TestArtifactRefV1:
    def test_construction(self):
        ref = ArtifactRefV1(
            artifact_id="art_001",
            path="s3://bucket/key",
            hash="a" * 64,
            mime_type="audio/mpeg",
        )
        assert ref.artifact_id == "art_001"
        assert ref.path == "s3://bucket/key"
        assert ref.hash == "a" * 64
        assert ref.mime_type == "audio/mpeg"
        assert isinstance(ref.created_at, datetime)

    def test_created_at_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        ref = ArtifactRefV1(
            artifact_id="art_001",
            path="s3://bucket/key",
            hash="a" * 64,
            mime_type="audio/mpeg",
        )
        after = datetime.now(timezone.utc)
        assert before <= ref.created_at <= after

    def test_is_frozen(self):
        ref = ArtifactRefV1(
            artifact_id="art_001",
            path="s3://bucket/key",
            hash="a" * 64,
            mime_type="audio/mpeg",
        )
        with pytest.raises(ValidationError):
            ref.path = "s3://bucket/other-key"

    @pytest.mark.parametrize(
        "missing_field",
        ["artifact_id", "path", "hash", "mime_type"],
    )
    def test_required_fields(self, missing_field):
        fields = {
            "artifact_id": "art_001",
            "path": "s3://bucket/key",
            "hash": "a" * 64,
            "mime_type": "audio/mpeg",
        }
        del fields[missing_field]
        with pytest.raises(ValidationError):
            ArtifactRefV1(**fields)

    @pytest.mark.parametrize("bad_hash", ["a" * 63, "a" * 65])
    def test_hash_must_be_64_chars(self, bad_hash):
        with pytest.raises(ValidationError):
            ArtifactRefV1(
                artifact_id="art_001",
                path="s3://bucket/key",
                hash=bad_hash,
                mime_type="audio/mpeg",
            )


class TestStageRecordV1:
    def test_defaults(self):
        stage = StageRecordV1(stage_id="S00")
        assert stage.stage_id == "S00"
        assert stage.status == StageStatus.PENDING
        assert stage.attempt == 1
        assert stage.started_at is None
        assert stage.completed_at is None
        assert stage.output_artifact_ids == []

    def test_explicit_values(self):
        now = datetime.now(UTC)
        stage = StageRecordV1(
            stage_id="S10",
            status=StageStatus.PASSED,
            attempt=2,
            started_at=now,
            completed_at=now,
            output_artifact_ids=["art_001", "art_002"],
        )
        assert stage.status == StageStatus.PASSED
        assert stage.attempt == 2
        assert stage.started_at == now
        assert stage.completed_at == now
        assert stage.output_artifact_ids == ["art_001", "art_002"]

    def test_status_rejects_invalid_value(self):
        with pytest.raises(ValidationError):
            StageRecordV1(stage_id="S00", status="not_a_status")

    def test_requires_stage_id(self):
        with pytest.raises(ValidationError):
            StageRecordV1()

    def test_output_artifact_ids_default_is_not_shared(self):
        stage_a = StageRecordV1(stage_id="S00")
        stage_b = StageRecordV1(stage_id="S10")
        stage_a.output_artifact_ids.append("art_001")
        assert stage_b.output_artifact_ids == []


class TestProductionManifestV1:
    def test_defaults(self):
        manifest = ProductionManifestV1(run_id="run_001", idea_request_id="idea_001")
        assert manifest.run_id == "run_001"
        assert manifest.idea_request_id == "idea_001"
        assert isinstance(manifest.created_at, datetime)
        assert manifest.stages == []

    def test_requires_run_id_and_idea_request_id(self):
        with pytest.raises(ValidationError):
            ProductionManifestV1()
        with pytest.raises(ValidationError):
            ProductionManifestV1(run_id="run_001")
        with pytest.raises(ValidationError):
            ProductionManifestV1(idea_request_id="idea_001")

    def test_with_stages(self):
        manifest = ProductionManifestV1(
            run_id="run_001",
            idea_request_id="idea_001",
            stages=[
                StageRecordV1(stage_id="S00", status=StageStatus.PASSED),
                StageRecordV1(stage_id="S10", status=StageStatus.RUNNING),
            ],
        )
        assert len(manifest.stages) == 2
        assert manifest.stages[0].stage_id == "S00"
        assert manifest.stages[1].status == StageStatus.RUNNING

    def test_json_round_trip(self):
        manifest = ProductionManifestV1(
            run_id="run_001",
            idea_request_id="idea_001",
            stages=[StageRecordV1(stage_id="S00")],
        )
        payload = manifest.model_dump_json()
        rebuilt = ProductionManifestV1.model_validate_json(payload)
        assert rebuilt == manifest
