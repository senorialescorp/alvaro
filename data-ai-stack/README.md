# data-ai-stack

Stack local de experimentacion: **JupyterLab + MLflow** conectados a un **Data Warehouse en SQL Server** (cargado por SSIS).

```
┌──────────────┐   ODBC 18    ┌──────────────────────┐
│  JupyterLab  │─────────────▶│  Data Warehouse      │
│  (:8888)     │              │  SQL Server / SSIS   │
└──────┬───────┘              └──────────────────────┘
       │ HTTP                          ▲
       ▼                               │ ODBC 18
┌──────────────┐              ┌────────┴─────┐
│  MLflow      │◀─────────────│  jobs        │
│  (:5000)     │              │  (batch)     │
└──────┬───────┘              └──────────────┘
       ▼
┌──────────────┐
│  Postgres    │  backend store de MLflow
└──────────────┘
```

## Estructura

| Ruta | Que es |
|---|---|
| `docker-compose.yml` | Orquestacion de todos los servicios |
| `.env` | Credenciales y puertos (no se versiona; copia de `.env.example`) |
| `mlflow/` | Dockerfile del tracking server (Postgres backend + artifacts locales) |
| `jupyter/` | Dockerfile de JupyterLab con ODBC Driver 18, pyodbc, jupysql, mlflow |
| `jobs/` | Dockerfile ligero para scripts batch (mismo driver ODBC) |
| `src/` | Codigo Python compartido. `src/dw.py` = conexion al DW |
| `src/jobs/` | Jobs ejecutables con `python -m src.jobs.<nombre>` |
| `notebooks/` | Notebooks (montado en `/home/jovyan/work`) |
| `sql/` | Consultas `.sql` reutilizables |
| `logs/` | Logs de cada servicio |

## Arranque

```bash
cp .env.example .env        # y edita DW_HOST / DW_DATABASE / DW_USER / DW_PASSWORD
docker compose up -d --build
```

- JupyterLab: http://localhost:8888 (token = `JUPYTER_TOKEN` del `.env`)
- MLflow UI:  http://localhost:5000

## Conectarse al DW

`DW_HOST` en `.env`:

| Donde esta el SQL Server | Valor |
|---|---|
| En tu Windows (host) | `host.docker.internal` |
| Servidor remoto | IP o hostname |
| Contenedor local de desarrollo | `dw` (ver abajo) |

Si usas SQL Server en el host, habilita TCP/IP en *SQL Server Configuration Manager*, puerto 1433, y autenticacion mixta (SQL login).

Desde un notebook:

```python
from src.dw import read_sql, read_sql_file, ping

ping()                                           # verifica conexion
df = read_sql("SELECT TOP 100 * FROM dbo.FactVentas")
df = read_sql_file("/home/jovyan/sql/ventas.sql", params={"anio": 2025})
```

O con la magic de jupysql:

```python
%load_ext sql
from src.dw import sqlalchemy_url
%sql {sqlalchemy_url()}
%sql SELECT TOP 10 * FROM dbo.DimFecha
```

## MLflow desde notebooks / jobs

`MLFLOW_TRACKING_URI=http://mlflow:5000` ya viene en el entorno. Solo:

```python
import mlflow
mlflow.set_experiment("mi-experimento")
with mlflow.start_run():
    mlflow.log_metric("rmse", 0.42)
```

Los artifacts se guardan en el volumen `mlflow_artifacts` y los sirve el propio server (`--serve-artifacts`), asi que los clientes no necesitan acceso al storage.

## Jobs batch

```bash
docker compose run --rm jobs python -m src.jobs.smoke_test   # prueba DW + MLflow
docker compose run --rm jobs python -m src.jobs.mi_job
```

## SQL Server local de desarrollo (opcional)

Si no tienes el DW a mano:

```bash
docker compose --profile local-dw up -d dw
```

y en `.env`: `DW_HOST=dw`, `DW_USER=sa`, `DW_PASSWORD=<MSSQL_SA_PASSWORD>`. Los scripts en `sql/` quedan montados en `/sql` dentro del contenedor para cargarlos con `sqlcmd`.

## Comandos utiles

```bash
docker compose logs -f mlflow
docker compose exec jupyter sqlcmd -S "$DW_HOST,$DW_PORT" -U "$DW_USER" -P "$DW_PASSWORD" -C -Q "SELECT @@VERSION"
docker compose down            # conserva volumenes
docker compose down -v         # borra Postgres de MLflow y artifacts
```
