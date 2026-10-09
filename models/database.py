from __future__ import annotations

import json
import os

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_FILE  = os.path.join(_PROJECT_ROOT, "db_config.json")

_DEFAULT_CONFIG: dict = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",
    "database": "clinic_db",
}

_pool: MySQLConnectionPool | None = None

def _load_config() -> dict:
    if not os.path.exists(_CONFIG_FILE):
        with open(_CONFIG_FILE, "w", encoding="utf-8") as fh:
            json.dump(_DEFAULT_CONFIG, fh, indent=4)
        return dict(_DEFAULT_CONFIG)
    with open(_CONFIG_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)

def init_pool() -> None:
    global _pool
    cfg = _load_config()
    _pool = MySQLConnectionPool(
        pool_name="clinic_pool",
        pool_size=5,
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=True,
    )

def get_connection():
    if _pool is None:
        raise RuntimeError("Pool not initialised. Call init_pool() first.")
    return _pool.get_connection()

def load_raw_config() -> dict:
    return _load_config()

def save_config(cfg: dict) -> None:
    with open(_CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=4)
