import sys
import re
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Nomes corretos (usando escapes Unicode para evitar corrupcao do PowerShell)
NOMES_CORRETOS = [
    "An\u00e1lise BP",
    "An\u00e1lise DFC",
    "An\u00e1lise Patrimonial (DVP)",
    "An\u00e1lise Or\u00e7ament\u00e1ria (BO)",
    "An\u00e1lise Financeira (BF)",
    "An\u00e1lise por Centro de Custos",
    "Demonstra\u00e7\u00e3o das Muta\u00e7\u00f5es do PL (DMPL)",
    "Integridade entre Demonstra\u00e7\u00f5es",
    "Confer\u00eancia das Demonstra\u00e7\u00f5es",
    "\u00cdndices de Liquidez",
    "Comparativo de Receitas",
    "Comparativo de Despesas",
    "Panorama de Resultados",
    "Custo de Pessoal",
]

def desaninhar(s):
    # Tenta re-decodificar como latin-1/utf-8 para desfazer mojibake
    for _ in range(5):
        try:
            novo = s.encode('latin-1').decode('utf-8')
            if novo == s:
                break
            s = novo
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return s

def normalizar(s):
    s = desaninhar(s)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

# Para cada elif nome_interno == "..."
padrao = re.compile(r'(elif nome_interno == )"([^"]+)"(:)')
resultados = []

def substituir(match):
    prefixo = match.group(1)
    valor_atual = match.group(2)
    sufixo = match.group(3)
    norm_atual = normalizar(valor_atual)
    for nome in NOMES_CORRETOS:
        if normalizar(nome) == norm_atual:
            if valor_atual != nome:
                resultados.append((valor_atual, nome))
                return f'{prefixo}"{nome}"{sufixo}'
            return match.group(0)
    resultados.append((valor_atual, "NAO_ENCONTRADO"))
    return match.group(0)

texto_novo, n = padrao.subn(substituir, texto)
arquivo.write_text(texto_novo, encoding="utf-8")

print(f"[INFO] Total de elif nome_interno processados: {n}")
for original, novo in resultados:
    if novo == "NAO_ENCONTRADO":
        print(f"  [AVISO] Nao encontrei correspondencia para: {repr(original)}")
    elif original != novo:
        print(f"  [OK] {repr(original)} -> {repr(novo)}")
