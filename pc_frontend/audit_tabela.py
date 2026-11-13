import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. ID DA TABELA PRINCIPAL ===")
# Procura todas as tabelas
tabelas = re.findall(r'<table[^>]*>', s)
for t in tabelas:
    print(f"  {t}")

print("\n=== 2. EXISTE UM TBODY DENTRO DA TABELA? ===")
if "<tbody>" in s:
    print("  SIM, existe <tbody> no HTML.")
else:
    print("  NÃO, não existe <tbody> explícito. O navegador cria um automaticamente, mas o JS pode não encontrar.")

print("\n=== 3. O SCRIPT INLINE ESTÁ NO HTML? ===")
if "<script>" in s and "function carregar()" in s:
    print("  SIM, o script inline está presente.")
else:
    print("  NÃO, o script inline não está no HTML.")
