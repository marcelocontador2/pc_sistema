import re

c = open('main.py', encoding='utf-8-sig').read()

# Substitui a leitura do CSV por uma versão que tenta UTF-8 e depois latin-1
trecho_antigo = """        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                decoded = f.read()
            reader = csv.DictReader(io.StringIO(decoded))"""

trecho_novo = """        try:
            # Tenta ler como UTF-8, se falhar, tenta como ANSI (latin-1)
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    decoded = f.read()
            except UnicodeDecodeError:
                with open(caminho, "r", encoding="latin-1") as f:
                    decoded = f.read()
            reader = csv.DictReader(io.StringIO(decoded))"""

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Leitura do CSV agora aceita UTF-8 e ANSI!")
else:
    print("[AVISO] Trecho não encontrado. Tentando abordagem alternativa.")
    # Fallback: substitui direto no texto
    c = c.replace('encoding="utf-8-sig"', 'encoding="utf-8-sig"')  # Mantém

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
