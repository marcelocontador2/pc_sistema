import re, shutil, datetime

arquivo = r"pc_backend\main.py"
backup = f"pc_backend\\main_backup_panorama_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    codigo = f.read()

padrao = re.compile(r'(async def api_panorama\(periodo: str\):.*?return \{"erro": "falha", "mensagem": str\(e\)\})', re.DOTALL)
match = padrao.search(codigo)

if not match:
    print("[ERRO] Nao foi possivel encontrar a funcao api_panorama no main.py.")
    exit()

funcao_antiga = match.group(0)

nova_funcao = '''async def api_panorama(periodo: str):
    try:
        import sqlite3, json, os
        from matriz_integridade import _limpar_valor
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        def buscar_no_banco(tipo):
            nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
            cursor.execute("SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?", (nome,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else []
            
        demonstrativos = {
            "BALANCO_PATRIMONIAL": "Balanço Patrimonial",
            "BALANCO_ORCAMENTARIO": "Balanço Orçamentário",
            "BALANCO_FINANCEIRO": "Balanço Financeiro",
            "DFC": "Demonstração do Fluxo de Caixa",
            "DVP": "Demonstração das Variações Patrimoniais",
            "DMPL": "Demonstração das Mutações do PL",
        }
        faltando = []
        for tipo, nome in demonstrativos.items():
            dados = buscar_no_banco(tipo)
            if not dados:
                faltando.append(nome)
        if faltando:
            conn.close()
            return {"erro": "faltando", "pecas": faltando}
            
        l_bp = buscar_no_banco("BALANCO_PATRIMONIAL")
        l_bo = buscar_no_banco("BALANCO_ORCAMENTARIO")
        l_dvp = buscar_no_banco("DVP")
        
        # Busca genérica (contém o termo)
        def buscar(linhas, termos):
            for p in linhas:
                for termo in termos:
                    termo_upper = termo.upper()
                    for col_espec in [0, 3]:
                        if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                            col_valor = col_espec + 1
                            if len(p) > col_valor:
                                try:
                                    v = abs(_limpar_valor(p[col_valor]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0
            
        # Busca EXATA (para evitar pegar "TOTAL DO PASSIVO" quando procura "TOTAL")
        def buscar_exato(linhas, termo_exato):
            for p in linhas:
                for col_espec in [0, 3]:
                    if len(p) > col_espec and str(p[col_espec]).strip().upper() == termo_exato.upper():
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except:
                                pass
            return 0.0

        # === BP ===
        passivo_total = buscar_exato(l_bp, "TOTAL DO PASSIVO")
        if passivo_total == 0.0:
            passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO", "PASSIVO TOTAL"])
            
        pl = buscar_exato(l_bp, "TOTAL DO PATRIMÔNIO LÍQUIDO")
        if pl == 0.0:
            pl = buscar_exato(l_bp, "TOTAL DO PATRIMONIO LIQUIDO")
        if pl == 0.0:
            pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"])
            
        ativo_total = buscar_exato(l_bp, "TOTAL")
        if ativo_total == 0.0:
            ativo_total = buscar(l_bp, ["TOTAL DO ATIVO", "ATIVO TOTAL"])
        if ativo_total == 0.0:
            ativo_total = passivo_total + pl
            
        caixa_bp = buscar(l_bp, ["CAIXA E EQUIVALENTES", "CAIXA E EQUIVALENTE"])
        superavit_financeiro = buscar(l_bp, ["SUPERÁVIT FINANCEIRO", "SUPERAVIT FINANCEIRO"])
        
        # === BO ===
        receita_realizada = buscar(l_bo, ["TOTAL DAS RECEITAS", "RECEITAS REALIZADAS", "RECEITA REALIZADA", "TOTAL DA RECEITA", "RECEITAS"])
        despesa_empenhada = buscar(l_bo, ["TOTAL DAS DESPESAS", "DESPESAS EMPENHADAS", "DESPESA EMPENHADA", "TOTAL DA DESPESA", "DESPESAS"])
        superavit_orcamentario = receita_realizada - despesa_empenhada
        
        # === DVP ===
        total_vpa = buscar(l_dvp, ["Total das Variações Ativas", "TOTAL DAS VARIACOES ATIVAS", "VARIAÇÕES ATIVAS"])
        total_vpd = buscar(l_dvp, ["Total das Variações Passivas", "TOTAL DAS VARIACOES PASSIVAS", "VARIAÇÕES PASSIVAS"])
        superavit_patrimonial = total_vpa - total_vpd
        
        conn.close()
        
        return {
            "ativo_total": ativo_total,
            "passivo_total": passivo_total,
            "patrimonio_liquido": pl,
            "caixa_bp": caixa_bp,
            "receita_realizada": receita_realizada,
            "despesa_empenhada": despesa_empenhada,
            "superavit_orcamentario": superavit_orcamentario,
            "superavit_patrimonial": superavit_patrimonial,
            "superavit_financeiro": superavit_financeiro,
        }
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}'''

codigo = codigo.replace(funcao_antiga, nova_funcao)

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(codigo)

print("[OK] Funcao api_panorama corrigida com Busca Exata!")
print("\n==============================================")
print("=== AÇÃO OBRIGATÓRIA: REINICIAR O SERVIDOR ===")
print("==============================================")
print("O Python precisa ser reiniciado para carregar a nova funcao.")
print("1. Vá no terminal do uvicorn, aperte Ctrl+C.")
print("2. Suba novamente: cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Na tela do navegador, aperte Ctrl+Shift+R, e clique em Verificar, Salvar e Exibir.")
