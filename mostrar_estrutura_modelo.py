import os

print("="*70)
print("📄 ESTRUTURA COMPLETA DO MODELO (TODAS AS PÁGINAS)")
print("="*70)

for i in range(1, 18):
    arquivo = f"modelo_pagina_{i}.html"
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        print(f"\n{'='*70}")
        print(f"📄 PÁGINA {i} - Tamanho: {len(conteudo)} caracteres")
        print(f"{'='*70}")
        # Mostra as primeiras 20 linhas (o suficiente para ver a estrutura)
        linhas = conteudo.split("\n")
        for linha in linhas[:20]:
            print(linha[:200])
        if len(linhas) > 20:
            print(f"... (mais {len(linhas) - 20} linhas)")
