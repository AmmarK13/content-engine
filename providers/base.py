"""
providers/base.py

Provider interface protocol definition.

Every provider — stub today, real vendor integration in M2 — satisfies this Protocol.
The graph only ever knows the capability name, never which concrete class satisfies it.
"""

from typing import Protocol, runtime_checkable

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1


@runtime_checkable
class StageProvider(Protocol):
    """
    Protocol definition for capability providers.

    Every provider (stub or real vendor) must define a capability string and a run
    method that accepts a StageEnvelopeV1 and returns a StageOutputV1.
    """

    capability: str

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        ...
