c = open("pc_frontend/analise_financeira_bf.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("ESTRUTURA DO HTML DO BF (tamanho: {} chars)".format(len(c)))
print("=" * 70)

# Mostra o topo (head e estilos)
print("--- TOPO (0-3000 chars) ---")
print(c[:3000])

print("\n--- MEIO / CARDS / TABELAS ---")
# Tenta achar as secoes principais
import re
for tag in ["<div class=\"cards\"", "<table", "<div id=\"tab\"", "<canvas", "<div class=\"grafico"]:
    idx = c.find(tag)
    if idx != -1:
        print(f"\n[Encontrado: {tag}] (posicao {idx})")
        print(c[idx:idx+800])

print("\n--- FIM DO ARQUIVO (ultimos 3000 chars) ---")
print(c[-3000:])
