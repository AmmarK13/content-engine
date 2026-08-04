from temporalio import activity

from contracts.common.envelope import StageEnvelopeV1
from contracts.common.manifest import StageRecordV1, StageStatus
from orchestrator.manifest_store import save_stage_record
from orchestrator.stage_executor import execute_stage


@activity.defn
async def run_stage(
    capability: str,
    envelope_dict: dict,
    run_id: str,
    idea_request_id: str,
) -> dict:
    envelope = StageEnvelopeV1.model_validate(envelope_dict)
    output, validation_ref = execute_stage(run_id, idea_request_id, capability, envelope)
    result = output.model_dump()
    # Pass validation_ref back so the pipeline can attach it to the next envelope
    result["_validation_ref"] = validation_ref.model_dump()
    return result


@activity.defn
async def record_g80_approval(
    run_id: str,
    idea_request_id: str,
    started_at: str,
    completed_at: str,
) -> None:
    """Persist the G80 human-approval gate as a manifest row."""
    save_stage_record(
        run_id=run_id,
        idea_request_id=idea_request_id,
        stage=StageRecordV1(
            stage_id="G80",
            status=StageStatus.PASSED,
            attempt=1,
            started_at=started_at,
            completed_at=completed_at,
        ),
    )