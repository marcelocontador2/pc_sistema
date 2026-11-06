c = open("pc_frontend/integridade.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("PROCURANDO FUNCAO QUE MONTA A TABELA (tbody, tr, td)")
print("=" * 70)

for i, ln in enumerate(c.split("\n"), 1):
    if 'tbody' in ln or 'tr' in ln or '<td' in ln or 'appendChild' in ln:
        print(f"Linha {i}: {ln.strip()[:200]}")

print("\n" + "=" * 70)
print("PROCURANDO FUNCAO QUE GERENCIA 'CONFERENCIA' OU NUMEROS (1)")
print("=" * 70)

for i, ln in enumerate(c.split("\n"), 1):
    if 'confer' in ln.lower() or 'erro' in ln.lower() or '(1)' in ln:
        print(f"Linha {i}: {ln.strip()[:200]}")
