import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_{ts}")

c = open("main.py", encoding="utf-8-sig").read()

nova_rota = '''def api_comparativo_despesas_v2(periodo_atual: str):
    import os
    upload_dir = r"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\uploads_raw"
    
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
        
    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0
        
    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0
        
    def ler_csv(periodo):
        if not periodo: return None
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_DESPESAS_{periodo_formatado}.csv")
        
        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_DESPESAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
                    
        if not os.path.exists(arquivo):
            return None
            
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f: linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f: linhas = f.readlines()
                
            dados = {
                "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
                "percentual_total": 0.0, "grupos": []
            }
            
            grupos_alvo = ["PESSOAL E ENCARGOS SOCIAIS", "OUTRAS DESPESAS CORRENTES", "INVESTIMENTOS"]
            
            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue
                
                nome = partes_linha[0].strip().strip('"').upper()
                
                if nome == "CREDITO DISPONÍVEL" or nome == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])
                    
                if nome in grupos_alvo:
                    if not any(g["nome"] == partes_linha[0].strip() for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": partes_linha[0].strip(),
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })
            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None
            
    atual = ler_csv(periodo_atual)
    anterior = ler_csv(periodo_anterior)
    
    if not atual:
        return {"erro": True, "mensagem": "Dados não encontrados para o período atual."}
        
    return {
        "erro": False,
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": []
        }
    }
'''

inicio = c.find('def api_comparativo_despesas_v2(periodo_atual: str):')
if inicio != -1:
    fim = c.find('@app.', inicio + 10)
    if fim == -1: fim = len(c)
    c = c[:inicio] + nova_rota + "\n\n" + c[fim:]
    open("main.py", "w", encoding="utf-8").write(c)
    print("[OK] Rota refeita com sucesso!")
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe OK!")
else:
    print("[ERRO] Rota não encontrada.")
