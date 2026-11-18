# pc_backend/main.py
"""
main.py - Ponto de entrada do backend.

Importa o app do main_legado.py, que registra TODAS as rotas.
O antigo `routers/dvp.py` (novo) foi removido porque duplicava as rotas
do `app/routers/dvp.py` (que ja funciona e tem o calculo do CSV).
"""
import sys
import os

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from pc_backend.main_legado import app

print("[main] App carregado do main_legado. Total de rotas:", len(app.routes))
