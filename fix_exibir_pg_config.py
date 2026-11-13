import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_exibir_pg_config")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função de buscar histórico
idx_inicio = conteudo.find('async def buscar_integridade_matriz(id: int):')
if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    # Substitui a função inteira, definindo o PG_CONFIG localmente
    nova_funcao = '''async def buscar_integridade_matriz(id: int):
    import json
    import psycopg2
    
    # Definição local para garantir que a variável exista
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado_json FROM historico_integridade_matriz WHERE id = %s", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row: 
            raise HTTPException(status_code=404, detail="Não encontrado")
            
        return json.loads(row[0])
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    print("✅ Função 'buscar_integridade_matriz' corrigida com PG_CONFIG local.")
else:
    print("❌ Função 'buscar_integridade_matriz' não encontrada no main.py.")

# Verifica se a sintaxe do arquivo inteiro está correta
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ Sintaxe do main.py verificada e salva com sucesso!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
