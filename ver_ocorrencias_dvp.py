c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("OCORRENCIAS DE 'analise_patrimonial' NO ARQUIVO")
print("=" * 70)

pos = 0
count = 0
while True:
    pos = c.find('analise_patrimonial', pos)
    if pos == -1:
        break
    count += 1
    # Mostra o contexto (100 chars antes e depois)
    inicio = max(0, pos - 150)
    fim = min(len(c), pos + 150)
    print(f"\n--- Ocorrencia {count} (posicao {pos}) ---")
    print(repr(c[inicio:fim]))
    pos += 1

print(f"\nTotal de ocorrencias: {count}")

print("\n" + "=" * 70)
print("SCRIPTS QUE ADICIONAM ITENS AO SUBMENU (textContent)")
print("=" * 70)
import re
for m in re.finditer(r'textContent\s*=\s*[\'"]([^\'"]+)[\'"]', c):
    print(f"  textContent = {m.group(1)}")
