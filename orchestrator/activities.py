from temporalio import activity 

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from orchestrator.registry import get as get_provider


@activity.defn
async def run_stage(capability: str, envelope_dict: dict) -> dict:
    """
    Look up the provider for `capability`, call it with the envelope,
    return the output as a dict.

    Args:
        capability: The capability name (e.g. "S10_script").
        envelope_dict: A StageEnvelopeV1.model_dump() dict.

    Returns:
        A StageOutputV1.model_dump() dict.
    """
    envelope = StageEnvelopeV1.model_validate(envelope_dict)
    provider = get_provider(capability)
    output: StageOutputV1 = provider.run(envelope)
    return output.model_dump()