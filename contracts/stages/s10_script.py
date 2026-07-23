"""
Output schema for S10 (script generation).
"""

from pydantic import BaseModel, Field


class ScriptPackageV1(BaseModel):
    """Output schema for S10 script generation, organized by scene."""

    run_id: str = Field(..., description="Which run this script belongs to")
    scenes: list[str] = Field(
        ..., min_length=1, description="Script text per scene, in order"
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    script = ScriptPackageV1(
        run_id="run_001",
        scenes=["Hey guys, welcome back.", "Today we discuss AI."],
    )
    print(script.model_dump_json(indent=2))