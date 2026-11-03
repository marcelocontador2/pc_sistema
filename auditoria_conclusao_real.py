import re

c = open(r"pc_frontend\relatorio_centro_custos.html", encoding="utf-8").read()

print("=" * 70)
print("BUSCANDO A SEÇÃO DE CONCLUSÃO NO HTML (NÃO NO JS)")
print("=" * 70)

# Procura por "conclusao-total" que é o ID do primeiro bloco
idx = c.find('id="conclusao-total"')
if idx != -1:
    print("\n[ENCONTRADO] O bloco 'conclusao-total' está no HTML.")
    # Mostra 500 chars antes e 500 depois
    inicio = max(0, idx - 800)
    fim = min(len(c), idx + 800)
    print(c[inicio:fim])
else:
    print("\n[FALTA] O bloco 'conclusao-total' NÃO foi encontrado no HTML.")

# Procura pela div que contém os blocos
print("\n" + "=" * 70)
print("BUSCANDO A DIV CONTAINER DA CONCLUSÃO")
print("=" * 70)
# Procura por qualquer div que tenha "conclusao" no id ou classe
matches = re.finditer(r'<div[^>]*id="[^"]*conclusao[^"]*"[^>]*>', c, re.IGNORECASE)
for m in matches:
    print(f"Encontrada: {m.group(0)}")

# Verifica se o título "Conclusão e Recomendações" está em algum lugar do HTML
print("\n" + "=" * 70)
print("BUSCANDO O TÍTULO 'Conclusão e Recomendações'")
print("=" * 70)
idx_titulo = c.find('Conclusão e Recomendações')
if idx_titulo != -1:
    inicio = max(0, idx_titulo - 500)
    fim = min(len(c), idx_titulo + 1000)
    print(c[inicio:fim])
else:
    print("Título não encontrado.")
