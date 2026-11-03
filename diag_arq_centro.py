import os, re

print("=" * 70)
print("ARQUIVOS RELACIONADOS A CENTRO DE CUSTOS")
print("=" * 70)

for f in os.listdir(r"pc_frontend"):
    if "centro" in f.lower() and f.endswith(".html"):
        print(f" - {f}")

print("\n" + "=" * 70)
print("COMO A TELA SALVA O HISTÓRICO")
print("=" * 70)
c = open(r"pc_frontend\analise_centro_custos.html", encoding="utf-8-sig").read()

# Procura a chamada de salvar histórico
match_salvar = re.search(r'fetch\([^)]*(?:salvar|historico)[^)]*\)', c, re.IGNORECASE)
if match_salvar:
    print(match_salvar.group(0))
else:
    print("Nenhuma chamada de salvar encontrada.")

print("\n" + "=" * 70)
print("A FUNÇÃO gerarPDF() ATUAL")
print("=" * 70)
match_func = re.search(r'function gerarPDF\(\) \{.*?\n        \}', c, re.DOTALL)
if match_func:
    print(match_func.group(0)[:500])
else:
    print("Função não encontrada.")
