import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Nome correto usando escape Unicode (evita corrupcao do PowerShell)
NOME_CORRETO = "\u00cdndices de Liquidez"  # Índices de Liquidez

# Substitui qualquer elif nome_interno que contenha "ndices de Liquidez" pelo nome correto
padrao = re.compile(r'(elif nome_interno == )"[^"]*ndices de Liquidez"(:)')
resultados = []

def substituir(match):
    resultados.append(match.group(0))
    return f'{match.group(1)}"{NOME_CORRETO}"{match.group(2)}'

texto_novo, n = padrao.subn(substituir, texto)
arquivo.write_text(texto_novo, encoding="utf-8")

print(f"[INFO] Total de elif Liquidez substituidos: {n}")
for r in resultados:
    print(f"  [OK] {r} -> elif nome_interno == \"{NOME_CORRETO}\":")
