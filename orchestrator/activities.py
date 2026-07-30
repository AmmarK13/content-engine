from temporalio import activity 

from contracts.common.envelope import StageEnvelopeV1
from orchestrator.stage_executor import execute_stage


@activity.defn
async def run_stage(run_id: str, capability: str, envelope_dict: dict) -> dict:
    """
    Execute a stage through the shared stage executor wrapper.

    Args:
        run_id: The pipeline run identifier.
        capability: The capability name (e.g. "S10_script").
        envelope_dict: A StageEnvelopeV1.model_dump() dict.

    Returns:
        A StageOutputV1.model_dump() dict.
    """
    envelope = StageEnvelopeV1.model_validate(envelope_dict)
    output = execute_stage(
        run_id=run_id,
        capability=capability,
        envelope_dict=envelope_dict,
        attempt=envelope.attempt,
    )
    return output.model_dump()