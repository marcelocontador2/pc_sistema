import sys, os, asyncio
sys.path.insert(0, os.path.abspath("pc_backend"))
from main import api_relatorio_consolidado_novo

r = asyncio.run(api_relatorio_consolidado_novo("2026-TRIMESTRE-3"))
print("status:", r.get("status"))
print("periodo:", r.get("periodo"))
print("\nENCONTRADOS:")
for e in r.get("encontrados", []):
    print(f"  - {e}")
print("\nFALTANDO:")
for f in r.get("faltando", []):
    print(f"  - {f}")
