"""Configuracao centralizada. Le de .env, com fallback para os valores atuais."""
import os
from pathlib import Path

# Carrega .env da raiz do projeto
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5433")),
    "database": os.getenv("PG_DATABASE", "pc_database"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "pc_admin_2026"),
}
