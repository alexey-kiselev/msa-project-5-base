import csv
import os
import sys
import psycopg2

DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://analytics:analytics@postgres:5432/analytics",
)
OUT_PATH = os.environ.get("OUTPUT_PATH", "/data/shipments.csv")


def main() -> int:
    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, client_id, driver_id, vehicle_id, status, created_at "
                "FROM shipments ORDER BY id"
            )
            rows = cur.fetchall()
            colnames = [d[0] for d in cur.description]
    finally:
        conn.close()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(rows)

    print(f"exported {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
