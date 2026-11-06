import sys, os
sys.path.insert(0, r"pc_backend")

# Importa a funcao diretamente
from integridade import analise_integridade
import asyncio

# Executa a funcao
resultado = asyncio.run(analise_integridade("2026-TRIMESTRE-3"))

# Mostra o resultado para o BP
for analise in resultado.get("analises", []):
    if "Balanço Patrimonial" in analise.get("titulo", ""):
        print("=" * 70)
        print("RESULTADO DIRETO DO integridade.py (sem FastAPI)")
        print("=" * 70)
        import json
        print(json.dumps(analise, indent=2, ensure_ascii=False))
        break
