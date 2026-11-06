import shutil, datetime

# Copia o BF como base
shutil.copy2("pc_frontend/analise_financeira_bf.html", "pc_frontend/analise_dfc.html")

# Le e altera
with open("pc_frontend/analise_dfc.html", "r", encoding="utf-8", errors="ignore") as f:
    c = f.read()

# Substituicoes globais
subs = [
    ("analise_financeira_bf", "analise_dfc"),
    ("Análise Financeira-BF", "Análise DFC"),
    ("analise_financeira_bf.html", "analise_dfc.html"),
    ("analise_bf", "analise_dfc"),
]

for antigo, novo in subs:
    c = c.replace(antigo, novo)

# Ajusta os titulos dos cards (Receitas -> Fluxo Operacional, etc.)
# (Ajuste fino: o render() ainda vai usar os campos que vieram da API, entao o backend precisa mandar os mesmos nomes)
# Vamos manter o mesmo formato de render para nao quebrar o JS

with open("pc_frontend/analise_dfc.html", "w", encoding="utf-8") as f:
    f.write(c)

print("[OK] HTML da DFC criado em pc_frontend/analise_dfc.html")
