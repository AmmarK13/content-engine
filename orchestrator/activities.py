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
    """
    Validate the envelope, run the stage through execute_stage (which
    handles manifest + telemetry recording), return the output as a dict.
    """
    envelope = StageEnvelopeV1.model_validate(envelope_dict)
    output = execute_stage(run_id, idea_request_id, capability, envelope)
    return output.model_dump()
