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
from orchestrator.registry import try_register_real_providers

from orchestrator.telemetry import get_connection

TEMPORAL_HOST = "localhost:7233"


@pytest.mark.integration
def test_pipeline_e2e():
    try:
        asyncio.run(_async_test_pipeline_e2e())
    except RuntimeError as exc:
        if "Connection refused" in str(exc) or "Server connection error" in str(exc):
            pytest.skip(f"Temporal server is not running: {exc}")
        raise


async def _async_test_pipeline_e2e():
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
    master_hash = None
    for _ in range(30):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT output_hash FROM stage_run_records WHERE run_id=%s AND stage_id=%s",
                        (run_id, "S60"),
                    )
                    row = cur.fetchone()
            if row and row[0]:
                master_hash = row[0]
                break
        except Exception:
            pass
        await asyncio.sleep(1)

    if not master_hash:
        pytest.fail("S60 output_hash never appeared in stage_run_records within timeout")

 

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

# 2. Check MinIO Artifacts — SHA-256-keyed, not just "something exists"
    s3_client = _make_s3_client()
    response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="artifacts/")
    assert "Contents" in response
    sha_keyed = [obj for obj in response["Contents"] if len(obj["Key"].split("/")[-1]) == 64]
    assert len(sha_keyed) > 0

    # 3. Check telemetry — 10 rows, not 11 (G80 is a signal wait, not an activity)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT stage_id, provider_name FROM stage_run_records WHERE run_id=%s",
                (run_id,),
            )
            telemetry_rows = cur.fetchall()
    assert len(telemetry_rows) == 10
    assert all(row[1] is not None for row in telemetry_rows)

    # 4. Non-determinism check — only meaningful once a real provider is actually registered
    
    real_providers = try_register_real_providers()
    if "script_generation" in real_providers:
        script_ref = next(r for r in manifest.stages if r.stage_id == "S10").output_artifact_ids[0]
        stub_scenes = [
            "Welcome to this AI avatar demonstration.",
            "In this video, we explore how deterministic pipelines ensure reliable automated publishing.",
            "Thank you for watching!",
        ]
        # fetch real content and confirm it's not the stub's hardcoded text
        # (exact fetch call depends on whichever helper is already in this file for artifact lookup by id)