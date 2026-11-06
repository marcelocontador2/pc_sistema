import re
c = open("pc_frontend/integridade.html", encoding="utf-8", errors="ignore").read()

# Procura o trecho onde ele renderiza "Conferência" ou coloca os parênteses (1)
print("=" * 70)
print("TRECHO QUE RENDERIZA A COLUNA CONFERÊNCIA / ERROS")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if "confer" in ln.lower() or "(1)" in ln or "erro" in ln.lower() or "diverg" in ln.lower():
        if "innerHTML" in ln or "td" in ln or "class" in ln:
            print(f"Linha {i}: {ln.strip()[:200]}")
