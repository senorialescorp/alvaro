# JupyterLab + conexion al Data Warehouse (SQL Server / SSIS) via ODBC Driver 18 + cliente MLflow.
# Base: jupyter/docker-stacks (Ubuntu 24.04, conda, pandas, scikit-learn, matplotlib, etc.)
ARG BASE_IMAGE=quay.io/jupyter/scipy-notebook:python-3.12
FROM ${BASE_IMAGE}

USER root

# Microsoft ODBC Driver 18 for SQL Server + sqlcmd/bcp (mssql-tools18)
ARG UBUNTU_VERSION=24.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates unixodbc unixodbc-dev \
 && curl -fsSL -o /tmp/packages-microsoft-prod.deb \
      "https://packages.microsoft.com/config/ubuntu/${UBUNTU_VERSION}/packages-microsoft-prod.deb" \
 && dpkg -i /tmp/packages-microsoft-prod.deb \
 && rm -f /tmp/packages-microsoft-prod.deb \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools18 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:/opt/mssql-tools18/bin" \
    PYTHONPATH="/home/${NB_USER}" \
    MLFLOW_TRACKING_URI="http://mlflow:5000"

COPY requirements.txt /tmp/requirements.txt

USER ${NB_UID}

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

WORKDIR /home/${NB_USER}/work
