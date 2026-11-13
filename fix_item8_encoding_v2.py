import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_item8_encoding_v2")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Faz o replace sem depender de colar os acentos no PowerShell.
# Usa a representação em bytes UTF-8 do mojibake para garantir a correspondência.

# Mapeamento mojibake -> UTF-8 correto (na ordem em que o Python salvou)
subs = [
    # Acentos comuns do mojibake (UTF-8 lido como Latin-1)
    ("TRANSFERÃŠNCIAS", "TRANSFERÊNCIAS"),
    ("TRANSFERÃNCIAS", "TRANSFERÊNCIAS"),
    ("TRANSFERÃ\u0160NCIAS", "TRANSFERÊNCIAS"),
    ("SERVIÃ‡OS", "SERVIÇOS"),
    ("SERVIÃ\u2021OS", "SERVIÇOS"),
    ("SERVIÃOS", "SERVIÇOS"),
    ("CONTRIBUIÃ‡Ã•ES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIÃ\u2021Ã\u2022ES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIÃ•ES", "CONTRIBUIÇÕES"),
    ("CONTRIBUIÃES", "CONTRIBUIÇÕES"),
    ("ÃŠ", "Ê"),   # fallback genérico
    ("Ã‡", "Ç"),   # fallback genérico
    ("Ã•", "Õ"),   # fallback genérico
]

# Aplica cada substituição e conta
total = 0
for antigo, novo in subs:
    if antigo in conteudo:
        n = conteudo.count(antigo)
        conteudo = conteudo.replace(antigo, novo)
        total += n
        print(f"  substituido: {repr(antigo)} -> {repr(novo)} ({n}x)")

print(f"Total de substituicoes: {total}")

# Depois das substituicoes, garante que grupos_nomes esteja na ordem da imagem (6 grupos)
# Procura o grupos_nomes na 1a funcao
import re
padrao_grupos = re.compile(r'grupos_nomes\s*=\s*\[[^\]]*\]')
ocorrencias = padrao_grupos.findall(conteudo)
print(f"\nOcorrencias de grupos_nomes encontradas: {len(ocorrencias)}")
for i, oc in enumerate(ocorrencias):
    print(f"  [{i+1}] {oc[:120]}")

# Se encontrou a lista, normaliza para os 6 grupos em ordem fixa
if ocorrencias:
    grupos_corretos = 'grupos_nomes = ["RECEITAS DE CONTRIBUIÇÕES", "RECEITAS PATRIMONIAIS", "RECEITAS DE SERVIÇOS", "TRANSFERÊNCIAS CORRENTES", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL"]'
    # Substitui a primeira ocorrencia (a da linha 4634)
    conteudo = padrao_grupos.sub(grupos_corretos, conteudo, count=1)
    print("\nOK: grupos_nomes da 1a funcao normalizado para 6 grupos em ordem.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("OK: main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"ERRO de sintaxe na linha {e.lineno}: {e.text}")
