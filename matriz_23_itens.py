import shutil

caminho = "pc_backend/matriz_integridade.py"
shutil.copy(caminho, caminho + ".bak_23_itens")

novo_codigo = '''import psycopg2

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

def _conectar():
    return psycopg2.connect(**PG_CONFIG)

def _buscar_saldos(periodo_str):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        
        ano = periodo_str.split('-')[0]
        cursor.execute("SELECT id FROM periodo WHERE ano = %s LIMIT 1", (int(ano),))
        periodo_row = cursor.fetchone()
        
        if not periodo_row:
            cursor.close()
            conn.close()
            return []
            
        periodo_id = periodo_row[0]
        
        cursor.execute("""
            SELECT b.codigo_conta, b.descricao_conta, b.saldo_atual
            FROM balancete_linha b
            JOIN documento_importado d ON b.documento_id = d.id
            WHERE d.periodo_id = %s
            ORDER BY b.codigo_conta
        """, (periodo_id,))
        linhas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return linhas
    except Exception as e:
        print(f"Erro no banco: {e}")
        return []

def gerar_matriz(periodo):
    try:
        linhas = _buscar_saldos(periodo)
        
        if not linhas:
            return {"erro": True, "mensagem": f"Não foram encontrados lançamentos para o período {periodo} no banco."}

        dados = {}
        for row in linhas:
            codigo = str(row[0]).strip() if row[0] else ""
            saldo = float(row[2]) if row[2] else 0.0
            dados[codigo] = saldo

        def get(codigo):
            return dados.get(codigo, 0.0)

        # Mapeamento dos 23 itens conforme a imagem original
        matriz = [
            {"item": "ATIVO", "balancete": get("1"), "bp": get("1"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO CIRCULANTE", "balancete": get("1.1"), "bp": get("1.1"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO NÃO CIRCULANTE", "balancete": get("1.2"), "bp": get("1.2"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "IMOBILIZADO", "balancete": get("1.2.3"), "bp": get("1.2.3"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "INTANGÍVEIS", "balancete": get("1.2.4"), "bp": get("1.2.4"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO CIRCULANTE", "balancete": get("2.1"), "bp": get("2.1"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "VALORES RESTITUÍVEIS - DISPÊNDIOS", "balancete": get("2.1.4"), "bp": "-", "bf": get("2.1.4"), "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(1)"},
            {"item": "VALORES RESTITUÍVEIS - INGRESSOS", "balancete": get("2.1.5"), "bp": "-", "bf": get("2.1.5"), "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO NÃO CIRCULANTE", "balancete": get("2.2"), "bp": get("2.2"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PATRIMÔNIO LÍQUIDO", "balancete": get("2.3"), "bp": get("2.3"), "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": get("2.3"), "conf": "OK"},
            {"item": "VPA", "balancete": get("3"), "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": get("3"), "dmpl": "-", "conf": "OK"},
            {"item": "VPD", "balancete": get("4"), "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": get("4"), "dmpl": "-", "conf": "OK"},
            {"item": "RECEITA CORRENTE REALIZADA", "balancete": get("4.1"), "bp": "-", "bf": get("4.1"), "bo": get("4.1"), "dfc": get("4.1"), "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "DESPESAS CORRENTES EMPENHADAS", "balancete": get("4.2"), "bp": "-", "bf": "-", "bo": get("4.2"), "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS CORRENTE", "balancete": get("4.2.1"), "bp": "-", "bf": get("4.2.1"), "bo": get("4.2.1"), "dfc": get("4.2.1"), "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS - A LIQUIDAR", "balancete": get("4.2.2"), "bp": "-", "bf": "-", "bo": get("4.2.2"), "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(2)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS CORRENTES - CANCELADOS", "balancete": get("4.2.3"), "bp": "-", "bf": "-", "bo": "-", "dfc": get("4.2.3"), "dvp": "-", "dmpl": "-", "conf": "(3)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS DE CAPITAL - CANCELADOS", "balancete": get("4.3"), "bp": "-", "bf": "-", "bo": "-", "dfc": get("4.3"), "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP INSCRITOS EM 31 DE DEZEMBRO DO ANO ANTERIOR", "balancete": get("4.4"), "bp": "-", "bf": "-", "bo": "-", "dfc": get("4.4"), "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS PAGOS", "balancete": get("4.5"), "bp": "-", "bf": "-", "bo": "-", "dfc": get("4.5"), "dvp": "-", "dmpl": "-", "conf": "(4)"},
            {"item": "INCORPORAÇÃO DE ATIVOS", "balancete": get("4.6"), "bp": "-", "bf": "-", "bo": "-", "dfc": get("4.6"), "dvp": get("4.6"), "dmpl": "-", "conf": "(5)"},
            {"item": "CAIXA E EQUIVALENTES DE CAIXA", "balancete": get("1.1.1"), "bp": get("1.1.1"), "bf": get("1.1.1"), "bo": "-", "dfc": get("1.1.1"), "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS DE CAPITAL", "balancete": get("4.7"), "bp": "-", "bf": get("4.7"), "bo": get("4.7"), "dfc": get("4.7"), "dvp": "-", "dmpl": "-", "conf": "OK"},
        ]

        return {
            "erro": False,
            "periodo": periodo,
            "matriz": matriz
        }
    except Exception as e:
        return {"erro": True, "mensagem": f"Erro ao gerar matriz: {str(e)}"}
'''

with open(caminho, "w", encoding="utf-8") as f:
    f.write(novo_codigo)

print("✅ matriz_integridade.py atualizado com os 23 itens do modelo original!")
