# Runner de jobs batch (entrenamiento, scoring, extracciones) que corren fuera de Jupyter.
# Mismo driver ODBC que el notebook, pero en una imagen ligera (python:3.12-slim).
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    MLFLOW_TRACKING_URI=http://mlflow:5000

ARG DEBIAN_VERSION=12
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates unixodbc \
 && curl -fsSL -o /tmp/packages-microsoft-prod.deb \
      "https://packages.microsoft.com/config/debian/${DEBIAN_VERSION}/packages-microsoft-prod.deb" \
 && dpkg -i /tmp/packages-microsoft-prod.deb \
 && rm -f /tmp/packages-microsoft-prod.deb \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN useradd --create-home --uid 1000 jobs \
 && mkdir -p /app/logs \
 && chown -R jobs:jobs /app
USER jobs

# El codigo se monta desde ./src en docker-compose; se sobreescribe con `command:`.
CMD ["python", "-m", "src.jobs.smoke_test"]
