import shutil
import ast
import re

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_item8_segunda_ocorrencia")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Lista de substituições mojibake -> UTF-8 (inclusive a variante "íŠ" e "í‡")
subs = [
    ("TRANSFERíŠNCIAS", "TRANSFERÊNCIAS"),
    ("TRANSFERíNCIAS", "TRANSFERÊNCIAS"),
    ("TRANSFERÃŠNCIAS", "TRANSFERÊNCIAS"),
    ("TRANSFERÃNCIAS", "TRANSFERÊNCIAS"),
    ("SERVIí‡OS", "SERVIÇOS"),
    ("SERVIíOS", "SERVIÇOS"),
    ("SERVIÃ‡OS", "SERVIÇOS"),
    ("SERVIÃOS", "SERVIÇOS"),
    ("CONTRIBUIí‡í•ES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIí‡íES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIÃ‡Ã•ES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIÃ•ES", "CONTRIBUIÇÕES"),
    ("íŠ", "Ê"),
    ("í‡", "Ç"),
    ("í•", "Õ"),
]

total = 0
for antigo, novo in subs:
    if antigo in conteudo:
        n = conteudo.count(antigo)
        conteudo = conteudo.replace(antigo, novo)
        total += n
        print(f"  substituido: {repr(antigo)} -> {repr(novo)} ({n}x)")

print(f"Total: {total} substituicoes")

# Agora normaliza a SEGUNDA ocorrência de grupos_nomes (a que ainda está com mojibake)
padrao_grupos = re.compile(r'grupos_nomes\s*=\s*\[[^\]]*\]')
ocorrencias = padrao_grupos.findall(conteudo)
print(f"\nOcorrencias de grupos_nomes depois das substituicoes: {len(ocorrencias)}")
for i, oc in enumerate(ocorrencias):
    print(f"  [{i+1}] {oc[:120]}")

grupos_corretos = 'grupos_nomes = ["RECEITAS DE CONTRIBUIÇÕES", "RECEITAS PATRIMONIAIS", "RECEITAS DE SERVIÇOS", "TRANSFERÊNCIAS CORRENTES", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL"]'

# Substitui TODAS as ocorrências pelo padrão correto (idempotente: se já está correto, substitui por igual)
conteudo = padrao_grupos.sub(grupos_corretos, conteudo)
print(f"\nOK: todas as {len(ocorrencias)} ocorrencias normalizadas para o padrao de 6 grupos.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("OK: main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"ERRO de sintaxe na linha {e.lineno}: {e.text}")
