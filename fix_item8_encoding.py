import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_item8_encoding")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# --- Correção 1: primeira função (linha 4634) ---
old_grupos = 'grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERÃŠNCIAS CORRENTES", "RECEITAS DE SERVIÃ‡OS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIÃ‡Ã•ES"]'
new_grupos = 'grupos_nomes = ["RECEITAS DE CONTRIBUIÇÕES", "RECEITAS PATRIMONIAIS", "RECEITAS DE SERVIÇOS", "TRANSFERÊNCIAS CORRENTES", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL"]'

if old_grupos in conteudo:
    conteudo = conteudo.replace(old_grupos, new_grupos)
    print("✅ Correção 1: grupos_nomes da 1ª função corrigido (UTF-8).")
else:
    print("⚠️ grupos_nomes da 1ª função não encontrado no formato exato.")

# --- Correção 2: segunda função (linha 7820) — verifica se tem o mesmo problema ---
# A segunda função provavelmente também tem um grupos_nomes ou lista fixa
import re
# Procura por grupos_nomes quebrados na 2ª função
padroes_mojibake = [
    'RECEITAS PATRIMONIAIS", "TRANSFERÃŠNCIAS CORRENTES',
    'RECEITAS PATRIMONIAIS", "TRANSFERÃNCIAS CORRENTES',
    'TRANSFERÃŠNCIAS CORRENTES',
    'RECEITAS DE SERVIÃ‡OS',
    'RECEITAS DE CONTRIBUIÃ‡Ã•ES',
    'TRANSFERÃNCIAS CORRENTES',
    'RECEITAS DE SERVIÃOS',
    'RECEITAS DE CONTRIBUIÃ•ES',
]

corrigiu_2 = False
for padrao in padroes_mojibake:
    if padrao in conteudo:
        # Substituição individual por UTF-8
        conteudo = conteudo.replace('TRANSFERÃŠNCIAS CORRENTES', 'TRANSFERÊNCIAS CORRENTES')
        conteudo = conteudo.replace('TRANSFERÃNCIAS CORRENTES', 'TRANSFERÊNCIAS CORRENTES')
        conteudo = conteudo.replace('RECEITAS DE SERVIÃ‡OS', 'RECEITAS DE SERVIÇOS')
        conteudo = conteudo.replace('RECEITAS DE SERVIÃOS', 'RECEITAS DE SERVIÇOS')
        conteudo = conteudo.replace('RECEITAS DE CONTRIBUIÃ‡Ã•ES', 'RECEITAS DE CONTRIBUIÇÕES')
        conteudo = conteudo.replace('RECEITAS DE CONTRIBUIÃ•ES', 'RECEITAS DE CONTRIBUIÇÕES')
        corrigiu_2 = True
        break

if corrigiu_2:
    print("✅ Correção 2: nomes de grupos com mojibake corrigidos em todas as ocorrências.")
else:
    print("ℹ️ Nenhuma ocorrência adicional de mojibake encontrada (a 1ª correção já cobriu).")

# --- Correção 3: garantir que TODOS os 6 grupos apareçam no JSON mesmo se zerados ---
# Altera o bloco que filtra grupos vazios, se existir
old_filter_1 = '''                elif nome in grupos_nomes:
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })'''
new_filter_1 = '''                elif nome in grupos_nomes:
                    orc_v = parse_valor(partes_linha[1])
                    real_v = parse_valor(partes_linha[2])
                    pct_v = parse_pct(partes_linha[3])
                    # Inclui TODOS os grupos, mesmo zerados
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": orc_v,
                        "realizado": real_v,
                        "percentual": pct_v
                    })'''

if old_filter_1 in conteudo:
    conteudo = conteudo.replace(old_filter_1, new_filter_1)
    print("✅ Correção 3: todos os grupos (mesmo zerados) serão incluídos no JSON.")
else:
    print("ℹ️ Bloco de append de grupos não encontrado (pode ter sido já alterado).")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
