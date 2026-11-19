import sys
import re
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Nome correto da Liquidez
NOME_LIQ = "\u00cdndices de Liquidez"  # Índices de Liquidez

# Encontra a linha do elif nome_interno para Liquidez (que contem \x8d ou caracteres de controle)
padrao = re.compile(r'(elif nome_interno == )"([^"]*ndices[^"]*)"(:)')
resultados = []

def substituir(match):
    prefixo = match.group(1)
    valor = match.group(2)
    sufixo = match.group(3)
    # Remove caracteres de controle
    valor_limpo = ''.join(c for c in valor if unicodedata.category(c) != 'Cc')
    resultados.append((valor, valor_limpo))
    return f'{prefixo}"{NOME_LIQ}"{sufixo}'

texto_novo, n = padrao.subn(substituir, texto)
arquivo.write_text(texto_novo, encoding="utf-8")

print(f"[INFO] Total de elif Liquidez processados: {n}")
for original, limpo in resultados:
    print(f"  [OK] {repr(original)} -> '{NOME_LIQ}'")
