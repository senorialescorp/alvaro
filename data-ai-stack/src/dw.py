"""Conexion al Data Warehouse (SQL Server / SSIS) via pyodbc + SQLAlchemy.

Lee la configuracion de las variables DW_* (ver .env). Uso:

    from src.dw import get_engine, read_sql, read_sql_file

    df = read_sql("SELECT TOP 100 * FROM dbo.FactVentas")
    df = read_sql_file("sql/ventas_mensuales.sql", params={"anio": 2025})
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

_engine: Engine | None = None


def odbc_connection_string() -> str:
    """Cadena ODBC construida desde el entorno."""
    driver = os.getenv("DW_DRIVER", "ODBC Driver 18 for SQL Server")
    return (
        "DRIVER={" + driver + "};"
        f"SERVER={os.environ['DW_HOST']},{os.getenv('DW_PORT', '1433')};"
        f"DATABASE={os.environ['DW_DATABASE']};"
        f"UID={os.environ['DW_USER']};"
        f"PWD={os.environ['DW_PASSWORD']};"
        f"Encrypt={os.getenv('DW_ENCRYPT', 'yes')};"
        f"TrustServerCertificate={os.getenv('DW_TRUST_SERVER_CERTIFICATE', 'yes')};"
    )


def sqlalchemy_url() -> str:
    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_connection_string())


def get_engine(**kwargs) -> Engine:
    """Engine singleton (pool compartido dentro del proceso)."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            sqlalchemy_url(),
            fast_executemany=True,
            pool_pre_ping=True,
            **kwargs,
        )
    return _engine


def read_sql(query: str, params: dict | None = None, **kwargs) -> pd.DataFrame:
    """Ejecuta una consulta y devuelve un DataFrame. Parametros con :nombre."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(query), conn, params=params, **kwargs)


def read_sql_file(path: str | Path, params: dict | None = None, **kwargs) -> pd.DataFrame:
    """Igual que read_sql pero leyendo la consulta desde un archivo .sql."""
    return read_sql(Path(path).read_text(encoding="utf-8"), params=params, **kwargs)


def ping() -> dict:
    """Comprobacion rapida de conectividad."""
    return read_sql(
        "SELECT @@SERVERNAME AS server_name, DB_NAME() AS database_name, "
        "@@VERSION AS version, SYSDATETIME() AS server_time"
    ).iloc[0].to_dict()
