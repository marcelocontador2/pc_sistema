c = open("pc_frontend/conferencia.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) FUNCAO QUE RENDERIZA A CONFERENCIA (render ou carregar)")
print("=" * 70)
# Procura a funcao que monta a tabela
import re
for m in re.finditer(r'function\s+(\w+)\s*\([^)]*\)\s*\{', c):
    nome = m.group(1)
    if 'render' in nome.lower() or 'carregar' in nome.lower() or 'exibir' in nome.lower() or 'tabela' in nome.lower():
        print(f"  Funcao encontrada: {nome}")
        # Pega o bloco da funcao
        inicio = m.start()
        fim = c.find('\nfunction ', inicio + 10)
        if fim == -1:
            fim = c.find('\n    </script>', inicio)
        if fim == -1:
            fim = inicio + 3000
        print(f"  Bloco:\n{c[inicio:fim][:2000]}")
        print("-" * 70)

print("\n" + "=" * 70)
print("2) ONDE O JSON DA API E PROCESSADO (fetch)")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'fetch(' in ln or 'response.json' in ln or 'data.analises' in ln:
        print(f"  Linha {i}: {ln.strip()[:150]}")
