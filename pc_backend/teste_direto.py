import sys
sys.path.insert(0, ".")
from main import api_custo_pessoal
import asyncio

try:
    resultado = asyncio.run(api_custo_pessoal("2026-TRIMESTRE-3", "COREN"))
    print("OK:", resultado)
except Exception as e:
    import traceback
    traceback.print_exc()
