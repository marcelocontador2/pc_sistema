import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# ---------------------------------------------------------
# PATCH 1: Normalizar TRIMESTRAL -> TRIMESTRE na rota salvar
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# PATCH 2: Normalizar TRIMESTRAL -> TRIMESTRE na API
# ---------------------------------------------------------
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
    fim_api = texto.find('\n@app', inicio_api + 10)
    if fim_api == -1: fim_api = len(texto)
    bloco = texto[inicio_api:fim_api]
    bloco = bloco.replace('f"%{periodo}%"', 'f"%{periodo_normalizado}%"')
    bloco = bloco.replace('(periodo,)', '(periodo_normalizado,)')
    texto = texto[:inicio_api] + bloco + texto[fim_api:]

# ---------------------------------------------------------
# PATCH 3: Corrigir leitura do DFC (usar "dados" como fallback)
# ---------------------------------------------------------
texto = texto.replace('dados_dfc = mod_dados.get("dados", {})', 
    'dados_dfc = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) and "dados" in mod_dados else mod_dados')

# ---------------------------------------------------------
# PATCH 4: Corrigir trigger da Liquidez (nome limpo)
# ---------------------------------------------------------
texto = texto.replace('elif nome_interno == "ÃÂndices de Liquidez":', 'elif nome_interno == "Índices de Liquidez":')
texto = texto.replace('elif nome_interno == "Ãndices de Liquidez":', 'elif nome_interno == "Índices de Liquidez":')

# Corrigir leitura da Liquidez para usar "dados"
padrao_liq = r'elif nome_interno == "Índices de Liquidez":\s*\n(\s+)liq = mod_dados\.get\("liquidez", \{\}\)'
import re
texto = re.sub(
    padrao_liq,
    r'elif nome_interno == "Índices de Liquidez":\n\1base = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) and "dados" in mod_dados else mod_dados\n\1liq = base.get("liquidez", {})',
    texto
)
texto = re.sub(r'(\s+)est = mod_dados\.get\("estrutura", \{\}\)', r'\1est = base.get("estrutura", {})', texto)
texto = re.sub(r'(\s+)liq_ant = mod_dados\.get\("liquidez_anterior", \{\}\)', r'\1liq_ant = base.get("liquidez_anterior", {})', texto)
texto = re.sub(r'(\s+)est_ant = mod_dados\.get\("estrutura_anterior", \{\}\)', r'\1est_ant = base.get("estrutura_anterior", {})', texto)
texto = re.sub(r'(\s+)val = mod_dados\.get\("valores", \{\}\)', r'\1val = base.get("valores", {})', texto)
texto = re.sub(r'(\s+)val_ant = mod_dados\.get\("valores_anterior", \{\}\)', r'\1val_ant = base.get("valores_anterior", {})', texto)

# Salvar
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Patches aplicados no arquivo main_legado.py (sem corromper acentos).")
