from datetime import datetime 
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StageStatus(str,Enum):
    #status of single stage

    PENDING= "pending"
    RUNNING  ="running"
    PASSED="passed"
    FAILED="failed"



class ArtifactRefV1(BaseModel):
    """
    A pointer to a stored file (audio, video, script, etc.) — never the
    file's actual bytes. The manifest and stage outputs should only ever
    reference artifacts this way.
    """
    artifact_id: str = Field(..., description="Unique ID for this artifact")
    storage_path: str = Field(..., description="Path/URI in the object store, e.g. s3://bucket/key")
    sha256: str = Field(..., description="SHA-256 hash of the file's exact contents")
    content_type: str = Field(..., description="e.g. audio/mpeg, video/mp4, application/json")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StageRecordV1(BaseModel):
    """One row of the manifest's per-stage checklist."""
    stage_id: str = Field(..., description="e.g. S00, S10, S20 ... G80, G90, S100")
    status: StageStatus = StageStatus.PENDING
    attempt: int = Field(default=1)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_artifact_ids: list[str] = Field(default_factory=list)


class ProductionManifestV1(BaseModel):
    """
    The central checklist record for one run — tracks the status of
    every stage/gate for this specific video from S00 through S100.
    """
    run_id: str = Field(..., description="Unique ID for this pipeline run")
    idea_request_id: str = Field(..., description="ID of the originating IdeaRequestV1")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    stages: list[StageRecordV1] = Field(default_factory=list)



if __name__ == "__main__":
    manifest = ProductionManifestV1(
        run_id="run_001",
        idea_request_id="idea_001"
    )

    print(manifest.model_dump_json(indent=2))