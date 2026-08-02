from temporalio import activity

from contracts.common.envelope import StageEnvelopeV1
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