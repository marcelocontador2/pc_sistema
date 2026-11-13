import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_add_dmpl_na_api")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Adiciona o DMPL no dicionário 'modulos'
old_modulos = '"centro_custos": "historico_centro_custos"\n    }'
new_modulos = '"centro_custos": "historico_centro_custos",\n        "dmpl": "historico_analise_dmpl"\n    }'
if old_modulos in conteudo:
    conteudo = conteudo.replace(old_modulos, new_modulos)
    print("✅ DMPL adicionado ao dicionário 'modulos'.")
else:
    print("❌ Não foi possível encontrar o final do dicionário 'modulos'.")

# 2. Adiciona o DMPL no dicionário 'nomes_amigaveis'
old_nomes = '"centro_custos": "Análise por Centro de Custos"\n    }'
new_nomes = '"centro_custos": "Análise por Centro de Custos",\n        "dmpl": "Demonstração das Mutações do PL (DMPL)"\n    }'
if old_nomes in conteudo:
    conteudo = conteudo.replace(old_nomes, new_nomes)
    print("✅ DMPL adicionado ao dicionário 'nomes_amigaveis'.")
else:
    print("❌ Não foi possível encontrar o final do dicionário 'nomes_amigaveis'.")

# 3. Como o DMPL não tem a coluna 'periodo' no mesmo formato, precisamos garantir que a busca funcione
# A tabela historico_analise_dmpl tem coluna 'periodo', então a busca padrão WHERE periodo = %s deve funcionar.
# Mas vamos verificar se precisamos de algum ajuste especial na query.
old_query = '''                if chave == "analise_financeira_bf":
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                else:
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))'''
                    
new_query = '''                if chave == "analise_financeira_bf":
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                elif chave == "dmpl":
                    # O DMPL pode ter o período em formato ligeiramente diferente, tenta LIKE
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                else:
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))'''

if old_query in conteudo:
    conteudo = conteudo.replace(old_query, new_query)
    print("✅ Query de busca do DMPL ajustada para usar LIKE.")
else:
    print("⚠️ Aviso: bloco de query não encontrado exatamente como esperado. Verifique manualmente se o DMPL precisa de LIKE.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
