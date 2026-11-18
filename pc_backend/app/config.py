import os

# Configuração do PostgreSQL
PG_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026",
}

# Caminhos base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "pc_frontend")
