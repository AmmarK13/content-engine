from __future__ import annotations

"""
providers/base.py

Base interfaces for stage providers.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1


@runtime_checkable
class StageProvider(Protocol):
    """Protocol that all stage providers must implement."""

    @property
    def capability(self) -> str:
        """The capability this provider implements (e.g., 'voice_synthesis')."""
        ...

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        """Execute the stage with the given envelope and return the output."""
        ...


# Abstract base class alternative (if you prefer ABC over Protocol)
class BaseStageProvider(ABC):
    """Abstract base class for stage providers."""

    @property
    @abstractmethod
    def capability(self) -> str:
        """The capability this provider implements."""
        pass

    @abstractmethod
    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        """Execute the stage with the given envelope and return the output."""
        pass