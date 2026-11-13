import re

print("=" * 70)
print("AUDITORIA DE HISTÓRICO: DMPL (FUNCIONA) vs CONFERÊNCIA (QUEBRADO)")
print("=" * 70)

# 1. DMPL - funcao carregarHistorico
with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    dmpl = f.read()

print("\n[1] DMPL - FUNÇÃO carregarHistorico:")
padrao = re.compile(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(dmpl)
if match:
    print(match.group(0)[:1500])
else:
    print("NÃO ENCONTRADA")

print("\n[2] DMPL - ROTAS FETCH RELACIONADAS AO HISTÓRICO:")
for m in re.finditer(r'fetch\(\s*[`\'"]([^`\'"]*historico[^`\'"]*)', dmpl, re.IGNORECASE):
    print(f"  - {m.group(1)}")

# 2. CONFERENCIA - funcao carregarHistorico
with open("conferencia.html", "r", encoding="utf-8") as f:
    conf = f.read()

print("\n[3] CONFERÊNCIA - FUNÇÃO carregarHistorico:")
padrao = re.compile(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(conf)
if match:
    print(match.group(0)[:1500])
else:
    print("NÃO ENCONTRADA")

print("\n[4] CONFERÊNCIA - ROTAS FETCH RELACIONADAS AO HISTÓRICO:")
for m in re.finditer(r'fetch\(\s*[`\'"]([^`\'"]*historico[^`\'"]*)', conf, re.IGNORECASE):
    print(f"  - {m.group(1)}")

print("\n[5] CONFERÊNCIA - BOTÕES (onclick):")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', conf):
    print(f"  - '{m.group(2).strip()}' -> {m.group(1)}")

print("\n[6] CONFERÊNCIA - IDs DE TABELAS:")
for m in re.finditer(r'<table[^>]*id="([^"]+)"', conf):
    print(f"  - {m.group(1)}")
