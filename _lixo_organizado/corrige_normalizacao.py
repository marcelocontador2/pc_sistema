import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Localiza a funcao da API
inicio = texto.find('async def api_relatorio_consolidado_novo(periodo: str):')
if inicio == -1:
    print("[ERRO] Funcao nao encontrada.")
    sys.exit(1)

# 2. Adiciona uma normalizacao logo no inicio da funcao
marcador = 'async def api_relatorio_consolidado_novo(periodo: str):'
posicao_insercao = texto.find('\n', inicio) + 1

normalizacao = '''
    # Normaliza o periodo: aceita TRIMESTRAL ou TRIMESTRE
    periodo_normalizado = periodo.replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE").replace("Trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo_normalizado.upper():
        partes = periodo_normalizado.upper().split("-")
        if len(partes) == 3:
            periodo_normalizado = f"{partes[0]}-TRIMESTRE-{partes[2]}"
    print(f"[API] Periodo original: {periodo} -> normalizado: {periodo_normalizado}")
'''

# Insere a normalizacao logo apos a definicao da funcao
texto = texto[:posicao_insercao] + normalizacao + texto[posicao_insercao:]

# 3. Substitui todas as ocorrencias de "%{periodo}%" por "%{periodo_normalizado}%"
# dentro da funcao da API
inicio_api = texto.find('async def api_relatorio_consolidado_novo')
fim_api = texto.find('\n@app', inicio_api + 10)
if fim_api == -1: fim_api = len(texto)

bloco_api = texto[inicio_api:fim_api]
bloco_api = bloco_api.replace('f"%{periodo}%"', 'f"%{periodo_normalizado}%"')
bloco_api = bloco_api.replace('(f"%{periodo}%",)', '(f"%{periodo_normalizado}%",)')
texto = texto[:inicio_api] + bloco_api + texto[fim_api:]

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Funcao da API corrigida para normalizar 'TRIMESTRAL' -> 'TRIMESTRE'.")
