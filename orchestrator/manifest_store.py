from psycopg import connect

from contracts.common.manifest import (
    ProductionManifestV1,
    StageRecordV1,
)


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "content_engine",
    "user": "temporal",
    "password": "temporal",
}


def get_connection():
    """Return a connection to the local PostgreSQL database."""
    return connect(**DB_CONFIG)


def save_manifest(manifest: ProductionManifestV1) -> None:
    """
    Persist a ProductionManifestV1 to PostgreSQL.

    Each StageRecordV1 is stored as one database row. Together,
    those rows represent the complete manifest for a pipeline run.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Store one row for every stage in the manifest.
            for stage in manifest.stages:
                cur.execute(
                    """
                    INSERT INTO manifest_stage_records (
                        run_id,
                        idea_request_id,
                        stage_id,
                        status,
                        attempt,
                        manifest_created_at,
                        started_at,
                        completed_at,
                        output_artifact_ids
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        manifest.run_id,
                        manifest.idea_request_id,
                        stage.stage_id,
                        stage.status.value,
                        stage.attempt,
                        manifest.created_at,
                        stage.started_at,
                        stage.completed_at,
                        stage.output_artifact_ids,
                    ),
                )

        # Persist all inserts as a single transaction.
        conn.commit()


def load_manifest(run_id: str) -> ProductionManifestV1:
    """
    Load a ProductionManifestV1 for the given pipeline run.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    idea_request_id,
                    manifest_created_at,
                    stage_id,
                    status,
                    attempt,
                    started_at,
                    completed_at,
                    output_artifact_ids
                FROM manifest_stage_records
                WHERE run_id = %s
                ORDER BY stage_id
                """,
                (run_id,),
            )

            rows = cur.fetchall()

    if not rows:
        raise ValueError(f"No manifest found for run_id '{run_id}'")

    stages = []

    # Reconstruct each StageRecordV1 from the database rows.
    for row in rows:
        stages.append(
            StageRecordV1(
                stage_id=row[2],
                status=row[3],
                attempt=row[4],
                started_at=row[5],
                completed_at=row[6],
                output_artifact_ids=row[7],
            )
        )

    # Manifest-level fields are identical across all rows, so take them
    # from the first row and attach the reconstructed stage records.
    return ProductionManifestV1(
        run_id=run_id,
        idea_request_id=rows[0][0],
        created_at=rows[0][1],
        stages=stages,
    )