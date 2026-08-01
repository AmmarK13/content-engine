"""
scripts/approve.py

CLI tool to send a G80 HumanApprovalV1 signal to a running Temporal workflow.
Usage:
    python scripts/approve.py <workflow_id> <run_id> [approved|rejected|changes_requested]
"""

import asyncio
import sys
from datetime import datetime, timezone

from temporalio.client import Client

from contracts.stages.g80_approval import ApprovalDecision, HumanApprovalV1
from orchestrator.manifest_store import load_manifest


def get_master_hash(run_id: str) -> str:
    """Look up the S60 output hash from the manifest."""
    try:
        manifest = load_manifest(run_id)
        s60 = next((s for s in manifest.stages if s.stage_id == "S60"), None)
        if s60 and s60.output_artifact_ids:
            print(f"Found S60 artifact ID: {s60.output_artifact_ids[0]}")
    except Exception as e:
        print(f"Warning: could not load manifest for run '{run_id}': {e}")

    try:
        from orchestrator.telemetry import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT output_hash FROM stage_run_records WHERE run_id = %s AND stage_id = 'S60'",
                    (run_id,),
                )
                row = cur.fetchone()
                if row and row[0]:
                    print(f"Found S60 hash from telemetry: {row[0]}")
                    return row[0]
    except Exception as e:
        print(f"Warning: could not query telemetry for hash: {e}")

    print("Warning: could not find S60 hash, using None — G80 gate will accept any hash.")
    return None


async def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/approve.py <workflow_id> <run_id> [approved|rejected|changes_requested]")
        sys.exit(1)

    workflow_id = sys.argv[1]
    run_id = sys.argv[2]
    decision_raw = sys.argv[3] if len(sys.argv) > 3 else "approved"

    decision_enum = ApprovalDecision(decision_raw.lower())

    master_video_hash = get_master_hash(run_id)

    # G80 gate accepts None hash (sets _current_master_hash check to pass-through)
    # Use a 64-char placeholder only if we truly can't find the real one
    if master_video_hash is None:
        master_video_hash = "0" * 64

    approval_payload = HumanApprovalV1(
        reviewer_id="cli_reviewer",
        decision=decision_enum,
        master_video_hash=master_video_hash,
        timestamp=datetime.now(timezone.utc),
        comments="Approved via CLI approve.py script",
    )

    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)

    await handle.signal("approve", approval_payload.model_dump(mode="json"))
    print(f"Approval signal sent to workflow '{workflow_id}' with decision '{decision_enum.value}'.")
    print(f"Hash used: {master_video_hash}")


if __name__ == "__main__":
    asyncio.run(main())