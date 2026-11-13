import re

with open("integridade.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNÇÃO carregarHistorico NA INTEGRIDADE ===")
match = re.search(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    print(bloco[:1200])
    
    # Verifica qual ID está sendo usado no innerHTML
    ids = re.findall(r'document\.getElementById\([\'"]([^\'"]+)[\'"]\)\.innerHTML', bloco)
    print("\n=== 2. IDs USADOS NO INNERHTML ===")
    for i in ids:
        print(f"  - {i}")
        if f'id="{i}"' in s:
            print(f"    -> OK: O ID '{i}' existe no HTML.")
        else:
            print(f"    -> ERRO: O ID '{i}' NÃO existe no HTML!")
else:
    print("Função carregarHistorico não encontrada no integridade.html")
