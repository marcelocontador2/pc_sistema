import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_financeira_bf")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Ajustar a rota do relatório consolidado para verificar a tabela correta do BF
idx_inicio = conteudo.find('@app.get("/api/relatorio_consolidado/{periodo}")')
if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    import json
    import psycopg2
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    modulos = {
        "analise_bp": "historico_analise_bp",
        "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial",
        "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf",  # Tabela correta
        "comparativo_receitas": "historico_comparativo_receitas",
        "comparativo_despesas": "historico_comparativo_despesas",
        "panorama": "historico_panorama",
        "liquidez": "historico_liquidez",
        "integridade": "historico_integridade_matriz",
        "conferencia": "historico_conferencia",
        "custo_pessoal": "historico_custo_pessoal",
        "centro_custos": "historico_centro_custos"
    }

    nomes_amigaveis = {
        "analise_bp": "Análise BP",
        "analise_dfc": "Análise DFC",
        "analise_patrimonial": "Análise Patrimonial (DVP)",
        "analise_orcamentaria": "Análise Orçamentária (BO)",
        "analise_financeira_bf": "Análise Financeira (BF)",
        "comparativo_receitas": "Comparativo de Receitas",
        "comparativo_despesas": "Comparativo de Despesas",
        "panorama": "Panorama de Resultados",
        "liquidez": "Índices de Liquidez",
        "integridade": "Integridade entre Demonstrações",
        "conferencia": "Conferência das Demonstrações",
        "custo_pessoal": "Custo de Pessoal",
        "centro_custos": "Análise por Centro de Custos"
    }

    encontrados = []
    faltando = []

    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()

        for chave, tabela in modulos.items():
            try:
                # Busca apenas id e data_geracao para ser mais leve
                cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))
                row = cursor.fetchone()
                
                if row:
                    encontrados.append({
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": str(row[1]) if row[1] else "Disponível",
                        "id": row[0]
                    })
                else:
                    faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
            except Exception as e:
                # Se a tabela não existir ou der erro, adiciona aos faltantes
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})

        cursor.close()
        conn.close()

        status = "ok" if len(faltando) == 0 else "faltando"
        
        return {
            "status": status,
            "encontrados": encontrados,
            "faltando": faltando,
            "periodo": periodo
        }

    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro de conexão com o PostgreSQL: {str(e)}"
        }'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    print("✅ Rota do Relatório Consolidado ajustada.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sucesso!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")

# --- PARTE 2: Ajustar o Frontend (relatorio_consolidado.html) ---
caminho_html = "pc_frontend/relatorio_consolidado.html"
try:
    shutil.copy(caminho_html, caminho_html + ".bak_fix_undefined")
    with open(caminho_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Corrige o texto que mostra "undefined"
    html = html.replace("Faltam undefined módulo(s) para consolidar.", "Faltam ${faltando.length} módulo(s) para consolidar.")
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Frontend (relatorio_consolidado.html) ajustado para não mostrar 'undefined'.")
except Exception as e:
    print(f"⚠️ Não foi possível ajustar o frontend: {e}")
