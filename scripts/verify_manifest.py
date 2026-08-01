"""
scripts/verify_manifest.py

Simple utility to inspect a persisted ProductionManifestV1 for a run.
"""

from __future__ import annotations

import sys

from orchestrator.manifest_store import load_manifest


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:")
        print("  uv run python scripts/verify_manifest.py <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    try:
        manifest = load_manifest(run_id)
    except Exception as exc:
        print(f"Failed to load manifest for run '{run_id}': {exc}")
        sys.exit(1)

    print(f"\nManifest for run: {manifest.run_id}")
    print(f"Idea request: {manifest.idea_request_id}")
    print(f"Created at : {manifest.created_at}")
    print(f"Total stages recorded: {len(manifest.stages)}")
    print()

    passed = 0

    for stage in manifest.stages:
        artifact_count = len(stage.output_artifact_ids)

        print(
            f"{stage.stage_id:6} | "
            f"{stage.status.value:8} | "
            f"attempt {stage.attempt} | "
            f"{artifact_count} artifact(s)"
        )

        if artifact_count:
            for artifact in stage.output_artifact_ids:
                print(f"    - {artifact}")

        if stage.status.value == "passed":
            passed += 1

    print()
    print(f"{passed}/{len(manifest.stages)} stages passed")


if __name__ == "__main__":
    main()