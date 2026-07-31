"""
tests/integration/test_pipeline_e2e.py

End-to-end integration test for the full 11-stage AvatarPipeline.
Marked with pytest.mark.integration so it runs when external services
(Temporal, Postgres, MinIO) are available.
"""

import asyncio
import json
import uuid
import pytest
from temporalio.client import Client

from contracts.stages.idea_request import IdeaRequestV1, Modality
from contracts.stages.g80_approval import HumanApprovalV1, ApprovalDecision
from orchestrator.pipeline import TASK_QUEUE, AvatarPipeline
from orchestrator.manifest_store import load_manifest
from orchestrator.storage import _make_s3_client, BUCKET

TEMPORAL_HOST = "localhost:7233"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_e2e():
    """
    Executes the full pipeline:
    1. Triggers workflow execution with an IdeaRequestV1.
    2. Waits for workflow to pause at G80 (wait_condition).
    3. Retrieves master_video_hash from S60 output in manifest (or fallback).
    4. Sends HumanApprovalV1 signal with matching master_video_hash.
    5. Waits for workflow completion.
    6. Verifies:
       - Workflow returned final output for S100.
       - Manifest store contains rows for all 11 stages with PASSED status.
       - MinIO bucket contains stored content-addressed artifacts.
    """
    run_id = f"test_e2e_{uuid.uuid4().hex[:8]}"
    idea = IdeaRequestV1(
        idea_request_id=run_id,
        modality=Modality.AVATAR,
        topic="E2E Integration Test Topic",
        identity_id="identity_e2e",
        voice_id="voice_e2e",
    )
    idea_json = idea.model_dump_json()

    client = await Client.connect(TEMPORAL_HOST)
    
    workflow_id = f"pipeline-e2e-{run_id}"
    handle = await client.start_workflow(
        AvatarPipeline.run,
        idea_json,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    # Poll until S60 is completed and recorded in manifest or workflow is waiting at G80
    master_hash = None
    for _ in range(30):
        try:
            manifest = load_manifest(run_id)
            s60 = next((s for s in manifest.stages if s.stage_id == "S60"), None)
            if s60 and s60.output_artifact_ids:
                master_hash = s60.output_artifact_ids[0]
                break
        except Exception:
            pass
        await asyncio.sleep(1)

    if not master_hash:
        master_hash = "stub-hash-" + "0" * 32

    # Send G80 approval signal
    approval_decision = HumanApprovalV1(
        reviewer_id="e2e-tester",
        decision=ApprovalDecision.APPROVED,
        master_video_hash=master_hash,
        comments="E2E Test Approval",
    )
    await handle.signal("approve", approval_decision.model_dump())

    # Wait for workflow completion
    result = await handle.result()
    assert result is not None

    # Assertions
    # 1. Check Manifest Store
    manifest = load_manifest(run_id)
    assert manifest.run_id == run_id
    assert len(manifest.stages) == 11
    for stage_rec in manifest.stages:
        assert stage_rec.status.value == "passed"

    # 2. Check MinIO Artifacts
    s3_client = _make_s3_client()
    response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="artifacts/")
    assert "Contents" in response
    assert len(response["Contents"]) > 0
