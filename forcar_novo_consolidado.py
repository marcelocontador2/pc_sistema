import sys, os, json, asyncio, sqlite3
sys.path.insert(0, os.path.abspath("pc_backend"))

from main import api_relatorio_consolidado_novo

# Chama a API diretamente (mesma função da rota)
resultado = asyncio.run(api_relatorio_consolidado_novo("2026-TRIMESTRE-3"))

print("=== RETORNO DA API ===")
print("Tipo:", type(resultado))
if isinstance(resultado, dict):
    print("Chaves:", list(resultado.keys()))
    dados = resultado.get("dados") or resultado.get("dados", {})
    if isinstance(dados, dict):
        print("Modulos no retorno da API:")
        for k in dados.keys():
            print(f"  - {k}")
        print()
        print("✅ DMPL no retorno!" if "dmpl" in dados else "❌ DMPL AUSENTE no retorno da API!")
    else:
        print("Tipo de 'dados':", type(dados))
        print("Conteudo:", str(dados)[:500])
else:
    print("Retorno:", str(resultado)[:500])
