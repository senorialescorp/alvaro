# MLflow Tracking Server
# Backend store: PostgreSQL (servicio mlflow-db). Artifacts: volumen local servido por el propio server (--serve-artifacts),
# asi los clientes (Jupyter, jobs) solo necesitan HTTP hacia MLflow y no acceso directo al storage.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MLFLOW_HOST=0.0.0.0 \
    MLFLOW_PORT=5000 \
    MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/db/mlflow.db \
    MLFLOW_ARTIFACTS_DESTINATION=/mlflow/artifacts \
    MLFLOW_WORKERS=2 \
    MLFLOW_ALLOWED_HOSTS="localhost,127.0.0.1,mlflow,mlflow:*,host.docker.internal,10.*,172.*,192.168.*"

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN useradd --create-home --uid 1000 mlflow \
 && mkdir -p /mlflow/artifacts /mlflow/db /mlflow/logs \
 && chown -R mlflow:mlflow /mlflow

USER mlflow
WORKDIR /mlflow
EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=5 \
  CMD curl -fsS "http://localhost:${MLFLOW_PORT}/health" || exit 1

# Shell form para expandir variables de entorno en runtime.
# --allowed-hosts: MLflow 3 bloquea DNS rebinding; hay que permitir el hostname interno "mlflow".
CMD mlflow server \
      --host "${MLFLOW_HOST}" \
      --port "${MLFLOW_PORT}" \
      --workers "${MLFLOW_WORKERS}" \
      --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
      --artifacts-destination "${MLFLOW_ARTIFACTS_DESTINATION}" \
      --allowed-hosts "${MLFLOW_ALLOWED_HOSTS}" \
      --serve-artifacts
