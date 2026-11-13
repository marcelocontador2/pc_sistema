import re
import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_consolidado_v2")

with open(caminho_main, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔧 INICIANDO CORREÇÃO DO RELATÓRIO CONSOLIDADO...\n")

# 1. Primeiro, vamos remover todas as definições antigas da função api_relatorio_consolidado_novo
# para não haver duplicatas.
linhas_novas = []
pular = False
contador_chaves = 0

for linha in linhas:
    # Detecta o início da função (seja a rota ou a definição)
    if "@app.get(\"/api/relatorio_consolidado/{" in linha or "async def api_relatorio_consolidado_novo(" in linha:
        if "def api_relatorio_consolidado_novo" in linha:
            pular = True
            contador_chaves = 0
        continue
    
    if pular:
        contador_chaves += linha.count("{") - linha.count("}")
        if contador_chaves <= 0 and "}" in linha:
            pular = False
        continue
    
    linhas_novas.append(linha)

# Junta o conteúdo novamente
conteudo = "".join(linhas_novas)

# 2. Agora, injeta a nova rota no final do arquivo (ou antes de um marcador específico)
# Vamos colocar logo após a definição da rota /relatorio_consolidado (HTML) ou no final do arquivo.

nova_funcao = '''
@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    import json
    import psycopg2
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    # Mapeamento dos módulos para as tabelas do PostgreSQL
    modulos = {
        "analise_bp": "historico_analise_bp",
        "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial",
        "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf",
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
                # Verifica se a tabela existe e tem dados para o período
                cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))
                row = cursor.fetchone()
                
                if row:
                    encontrados.append({
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponível",
                        "id": row[0]
                    })
                else:
                    faltando.append({
                        "nome": nomes_amigaveis.get(chave, chave)
                    })
            except Exception as e:
                # Se a tabela não existir ou der erro, adiciona aos faltantes
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})

        cursor.close()
        conn.close()

        # Monta o retorno no formato que o frontend espera
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
        }
'''

# Vamos inserir a função antes do último fechamento do arquivo (ou em local seguro)
# Para evitar erros, vamos adicionar ao final do arquivo.
conteudo += "\n\n" + nova_funcao

# Verifica a sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py atualizado e sintaxe verificada com sucesso!")
    print("✅ A rota do Relatório Consolidado agora busca os dados no PostgreSQL.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
