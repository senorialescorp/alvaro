"""Prueba de humo: conecta al DW, lee metadatos y registra un run en MLflow.

    docker compose run --rm jobs python -m src.jobs.smoke_test
"""
from __future__ import annotations

import logging
import os
import sys

import mlflow

from src.dw import ping, read_sql

log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, "smoke_test.log")),
    ],
)
log = logging.getLogger("smoke_test")


def main() -> int:
    log.info("MLFLOW_TRACKING_URI=%s", os.getenv("MLFLOW_TRACKING_URI"))
    log.info("DW_HOST=%s DW_DATABASE=%s", os.getenv("DW_HOST"), os.getenv("DW_DATABASE"))

    info = ping()
    log.info("Conectado a %s / %s", info["server_name"], info["database_name"])

    tables = read_sql(
        "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY 1, 2"
    )
    log.info("Tablas visibles en el DW: %d", len(tables))

    mlflow.set_experiment("smoke-test")
    with mlflow.start_run(run_name="dw-connectivity"):
        mlflow.log_param("dw_host", os.getenv("DW_HOST"))
        mlflow.log_param("dw_database", info["database_name"])
        mlflow.log_metric("dw_table_count", len(tables))
        mlflow.log_text(tables.to_csv(index=False), "dw_tables.csv")
    log.info("Run registrado en MLflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
