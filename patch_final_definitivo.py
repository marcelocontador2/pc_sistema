import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# =====================================================
# PATCH A: Normalizar TRIMESTRAL -> TRIMESTRE na rota salvar
# =====================================================
inicio_salvar = texto.find('async def salvar_relatorio_consolidado_novo(periodo: str):')
if inicio_salvar != -1:
    pos = texto.find('\n', inicio_salvar) + 1
    norm = '''    periodo = periodo.replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo.upper():
        partes = periodo.upper().split("-")
        if len(partes) == 3:
            periodo = f"{partes[0]}-TRIMESTRE-{partes[2]}"
'''
    texto = texto[:pos] + norm + texto[pos:]
    print("[OK] Patch A: normalizacao na rota salvar")

# =====================================================
# PATCH B: Normalizar TRIMESTRAL -> TRIMESTRE na API
# =====================================================
inicio_api = texto.find('async def api_relatorio_consolidado_novo(periodo: str):')
if inicio_api != -1:
    pos = texto.find('\n', inicio_api) + 1
    norm = '''    periodo_normalizado = periodo.replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo_normalizado.upper():
        partes = periodo_normalizado.upper().split("-")
        if len(partes) == 3:
            periodo_normalizado = f"{partes[0]}-TRIMESTRE-{partes[2]}"
'''
    texto = texto[:pos] + norm + texto[pos:]
    # Substituir buscas na API
    fim_api = texto.find('\n@app', inicio_api + 10)
    if fim_api == -1: fim_api = len(texto)
    bloco = texto[inicio_api:fim_api]
    bloco = bloco.replace('f"%{periodo}%"', 'f"%{periodo_normalizado}%"')
    bloco = bloco.replace('(periodo,)', '(periodo_normalizado,)')
    texto = texto[:inicio_api] + bloco + texto[fim_api:]
    print("[OK] Patch B: normalizacao na API")

# =====================================================
# PATCH C: Corrigir DFC (procurar dados em 'dados' se existir)
# =====================================================
# O template original faz: dados_dfc = ... (extrai de dados_item)
# Precisamos garantir que ele use dados_item.get("dados", dados_item)
padrao_dfc = re.compile(
    r'(dados_dfc\s*=\s*)dados_item(\s*\n)',
    re.DOTALL
)
if padrao_dfc.search(texto):
    texto = padrao_dfc.sub(r'\1dados_item.get("dados", dados_item) if isinstance(dados_item, dict) and "dados" in dados_item else dados_item\2', texto, count=1)
    print("[OK] Patch C: DFC agora le 'dados' corretamente")
else:
    print("[AVISO] Patch C: padrao 'dados_dfc = dados_item' nao encontrado")

# =====================================================
# PATCH D: Corrigir trigger da Liquidez e leitura
# =====================================================
# Corrigir o nome corrompido
texto = texto.replace('elif nome_interno == "ÃÂndices de Liquidez":', 'elif nome_interno == "Índices de Liquidez":')
texto = texto.replace('elif nome_interno == "Ãndices de Liquidez":', 'elif nome_interno == "Índices de Liquidez":')

# Na leitura da Liquidez, usar 'dados' como fallback
texto = re.sub(
    r'(elif nome_interno == "Índices de Liquidez":\s*\n)(\s+)liq = mod_dados\.get\("liquidez", \{\}\)',
    r'\1\2base_l = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) and "dados" in mod_dados else mod_dados\n\2liq = base_l.get("liquidez", {})',
    texto
)
texto = re.sub(r'(\s+)est = mod_dados\.get\("estrutura", \{\}\)', r'\1est = base_l.get("estrutura", {})', texto)
texto = re.sub(r'(\s+)liq_ant = mod_dados\.get\("liquidez_anterior", \{\}\)', r'\1liq_ant = base_l.get("liquidez_anterior", {})', texto)
texto = re.sub(r'(\s+)est_ant = mod_dados\.get\("estrutura_anterior", \{\}\)', r'\1est_ant = base_l.get("estrutura_anterior", {})', texto)
texto = re.sub(r'(\s+)val = mod_dados\.get\("valores", \{\}\)', r'\1val = base_l.get("valores", {})', texto)
texto = re.sub(r'(\s+)val_ant = mod_dados\.get\("valores_anterior", \{\}\)', r'\1val_ant = base_l.get("valores_anterior", {})', texto)
print("[OK] Patch D: trigger e leitura da Liquidez corrigidos")

# Salvar
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
