import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_relatorio_consolidado")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Função auxiliar para substituir o corpo de uma função
def substituir_funcao(nome_funcao, nova_funcao):
    global conteudo
    idx = conteudo.find(f"async def {nome_funcao}(")
    if idx == -1:
        idx = conteudo.find(f"def {nome_funcao}(")
    
    if idx != -1:
        i = conteudo.find("{", idx)
        c = 1
        i += 1
        while i < len(conteudo) and c > 0:
            if conteudo[i] == "{": c += 1
            elif conteudo[i] == "}": c -= 1
            i += 1
        conteudo = conteudo[:idx] + nova_funcao + conteudo[i:]
        print(f"✅ Função '{nome_funcao}' atualizada.")
    else:
        print(f"⚠️ Função '{nome_funcao}' não encontrada.")

# 1. Rota do Comparativo de Receitas
nova_receitas = '''async def verificar_comparativo_receitas(periodo: str):
    import psycopg2
    PG_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database", "user": "postgres", "password": "pc_admin_2026"}
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM historico_comparativo_receitas WHERE periodo = %s LIMIT 1", (periodo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"ok": True, "encontrado": bool(row), "data_geracao": "Disponível" if row else None}
    except Exception as e:
        return {"ok": False, "erro": str(e)}'''
substituir_funcao("verificar_comparativo_receitas", nova_receitas)

# 2. Rota do Comparativo de Despesas
nova_despesas = '''async def verificar_comparativo_despesas(periodo: str):
    import psycopg2
    PG_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database", "user": "postgres", "password": "pc_admin_2026"}
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM historico_comparativo_despesas WHERE periodo = %s LIMIT 1", (periodo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"ok": True, "encontrado": bool(row), "data_geracao": "Disponível" if row else None}
    except Exception as e:
        return {"ok": False, "erro": str(e)}'''
substituir_funcao("verificar_comparativo_despesas", nova_despesas)

# 3. Rota do Centro de Custos
nova_centro_custos = '''async def verificar_centro_custos(periodo: str):
    import psycopg2
    PG_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database", "user": "postgres", "password": "pc_admin_2026"}
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM historico_centro_custos WHERE periodo = %s LIMIT 1", (periodo,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"ok": True, "encontrado": bool(row), "data_geracao": "Disponível" if row else None}
    except Exception as e:
        return {"ok": False, "erro": str(e)}'''
substituir_funcao("verificar_centro_custos", nova_centro_custos)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sucesso! Sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
