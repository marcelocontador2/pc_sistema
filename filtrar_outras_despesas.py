import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_filtro_outras_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza a função api_comparativo_despesas_v2
inicio = c.find('def api_comparativo_despesas_v2(periodo_atual: str):')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
    exit(1)

fim = c.find('@app.', inicio + 10)
if fim == -1: fim = len(c)

nova_func = '''def api_comparativo_despesas_v2(periodo_atual: str):
    import os, unicodedata
    upload_dir = r"C:\\\\Users\\\\Marcelo Medeiros\\\\pc_sistema\\\\pc_storage\\\\uploads_raw"
    
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
        
    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip(\'"\').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0
        
    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip(\'"\').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0
        
    def normalizar(txt):
        return unicodedata.normalize(\'NFKD\', txt).encode(\'ASCII\', \'ignore\').decode(\'utf-8\').strip().upper()
        
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
                "percentual_total": 0.0, "grupos": [], "detalhes": []
            }
            
            grupos_alvo = [
                "PESSOAL E ENCARGOS SOCIAIS",
                "JUROS E ENCARGOS DA DIVIDA",
                "OUTRAS DESPESAS CORRENTES",
                "INVESTIMENTOS",
                "INVERSOES FINANCEIRAS",
                "AMORTIZACAO DA DIVIDA"
            ]
            grupos_alvo_norm = [normalizar(g) for g in grupos_alvo]
            
            # Para o Top 10, coletamos subgrupos DENTRO de Outras Despesas Correntes
            detalhes_temp = []
            dentro_outras = False
            nivel_outras = 0
            
            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue
                
                nome_original = partes_linha[0].strip().strip(\'"\')
                nome_norm = normalizar(nome_original)
                
                if not nome_original or len(nome_original) < 3: continue
                
                # Total Global
                if nome_norm == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])
                    
                # Grupos contábeis
                if nome_norm in grupos_alvo_norm:
                    if not any(g["nome"] == nome_original for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })
                
                # Marca quando entramos em OUTRAS DESPESAS CORRENTES
                if nome_norm == "OUTRAS DESPESAS CORRENTES":
                    dentro_outras = True
                    continue  # Pula a linha do grupo principal
                
                # Marca quando saímos (entramos em outro grupo de mesmo nível)
                if dentro_outras and nome_norm in grupos_alvo_norm:
                    dentro_outras = False
                    continue
                
                # Se estamos dentro de Outras Despesas Correntes, adiciona detalhes
                if dentro_outras:
                    valor_emp = parse_valor(partes_linha[2])
                    if valor_emp > 0:
                        detalhes_temp.append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": valor_emp,
                            "percentual": parse_pct(partes_linha[3])
                        })
            
            # Ordena por empenhado desc e pega top 10
            detalhes_temp.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = detalhes_temp[:10]
            
            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None
            
    atual = ler_csv(periodo_atual)
    anterior = ler_csv(periodo_anterior)
    
    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}
        
    return {
        "erro": False,
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": [], "detalhes": []
        }
    }
'''

c = c[:inicio] + nova_func + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
