"""
Configuracao centralizada do pc_sistema.

Detecta a raiz do projeto automaticamente e expoe paths absolutos
para evitar strings hardcoded nos scripts de patch.
"""
from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Raiz do projeto
# ---------------------------------------------------------------------------
# config.py esta em: pc_sistema/pc_backend/app/config.py
#   parents[0] = pc_backend/app
#   parents[1] = pc_backend
#   parents[2] = pc_sistema   <-- RAIZ
RAIZ: Path = Path(os.environ.get("PC_RAIZ", Path(__file__).resolve().parents[2]))


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
PC_BACKEND: Path = RAIZ / "pc_backend"
APP_DIR:    Path = PC_BACKEND / "app"
ROUTERS:    Path = APP_DIR / "routers"
SERVICES:   Path = APP_DIR / "services"
ANALYTICS:  Path = APP_DIR / "analytics"
INGESTION:  Path = APP_DIR / "ingestion"
CORE:       Path = PC_BACKEND / "core"
FONTS:      Path = PC_BACKEND / "fonts"
TESTS:      Path = PC_BACKEND / "tests"


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
PC_FRONTEND: Path = RAIZ / "pc_frontend"


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
PC_STORAGE:      Path = RAIZ / "pc_storage"
UPLOADS_RAW:     Path = PC_STORAGE / "uploads_raw"
UPLOADS_LOGOS:   Path = PC_STORAGE / "uploads_logos"
TEMP_DOWNLOADS:  Path = PC_STORAGE / "temp_downloads"


# ---------------------------------------------------------------------------
# Arquivos especificos
# ---------------------------------------------------------------------------
DVP_PY: Path = ROUTERS / "dvp.py"


# ---------------------------------------------------------------------------
# Diretorios temporarios / de trabalho (locais, nao versionados)
# ---------------------------------------------------------------------------
TEMP_DIR:   Path = RAIZ / "_tmp"
BACKUP_DIR: Path = RAIZ / "_backups_zip"


# ---------------------------------------------------------------------------
# Ambiente
# ---------------------------------------------------------------------------
ENV_FILE: Path = RAIZ / ".env"
ENV: str = os.environ.get("PC_ENV", "dev")  # dev | prod | test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def garantir_dirs() -> None:
    """Cria diretorios de trabalho se nao existirem."""
    for d in (TEMP_DIR, BACKUP_DIR):
        d.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    """Retorna o path relativo a raiz do projeto (para logs)."""
    try:
        return str(path.relative_to(RAIZ))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Diagnostico rapido: python -m pc_backend.app.config
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"RAIZ        = {RAIZ}")
    print(f"PC_BACKEND  = {PC_BACKEND}")
    print(f"APP_DIR     = {APP_DIR}")
    print(f"ROUTERS     = {ROUTERS}")
    print(f"SERVICES    = {SERVICES}")
    print(f"ANALYTICS   = {ANALYTICS}")
    print(f"INGESTION   = {INGESTION}")
    print(f"CORE        = {CORE}")
    print(f"FONTS       = {FONTS}")
    print(f"PC_FRONTEND = {PC_FRONTEND}")
    print(f"PC_STORAGE  = {PC_STORAGE}")
    print(f"TEMP_DIR    = {TEMP_DIR}")
    print(f"BACKUP_DIR  = {BACKUP_DIR}")
    print(f"ENV         = {ENV}")
    print()
    print(f"DVP_PY existe?     {DVP_PY.exists()}")
    print(f"FONTS existe?      {FONTS.exists()}")
    print(f"FRONTEND existe?   {PC_FRONTEND.exists()}")

# ---------------------------------------------------------------------------
# PostgreSQL - configuracao de conexao
# ---------------------------------------------------------------------------
# Le do .env se disponivel, senao usa defaults do ambiente de dev.
# Para carregar o .env automaticamente, use: pip install python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except ImportError:
    pass  # python-dotenv nao instalado - segue com defaults


PG_CONFIG: dict = {
    "host":     os.environ.get("PG_HOST", "localhost"),
    "port":     int(os.environ.get("PG_PORT", "5433")),
    "database": os.environ.get("PG_DATABASE", "pc_database"),
    "user":     os.environ.get("PG_USER", "postgres"),
    "password": os.environ.get("PG_PASSWORD", ""),
}


# ---------------------------------------------------------------------------
# Compatibilidade com codigo legado
# ---------------------------------------------------------------------------
BASE_DIR = str(PC_BACKEND)
UPLOAD_DIR = str(UPLOADS_RAW)
FRONTEND_DIR = str(PC_FRONTEND)