import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_contas_analiticas_{ts}")
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
            
            # Coleta TODAS as linhas com valor empenhado > 0
            # Depois filtra as que são contas analíticas (não têm subordinados)
            todas_linhas = []
            
            for idx, linha in enumerate(linhas):
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
                
                # Guarda TODAS as linhas para depois filtrar
                valor_emp = parse_valor(partes_linha[2])
                if valor_emp > 0:
                    todas_linhas.append({
                        "idx": idx,
                        "nome": nome_original,
                        "orcado": parse_valor(partes_linha[1]),
                        "empenhado": valor_emp,
                        "percentual": parse_pct(partes_linha[3])
                    })
            
            # Agora identifica as contas analíticas (linhas folha)
            # Uma conta é folha se a PRÓXIMA linha com valor NÃO é subordinada a ela
            # Heurística: uma linha é folha se não existe uma linha posterior que comece com ela + " - " ou seja continuação
            
            # Estratégia: pegar linhas que NÃO são cabeçalhos (não têm filhos)
            # Filtrar as linhas que aparecem como prefixo de outras
            contas_folha = []
            
            for i, l in enumerate(todas_linhas):
                nome_atual = l["nome"]
                eh_cabecalho = False
                
                # Verifica se a próxima linha é um subgrupo (começa com nome_atual ou é continuação)
                for j in range(i + 1, min(i + 5, len(todas_linhas))):
                    proxima = todas_linhas[j]
                    # Se a próxima tem o mesmo nome ou começa com o nome atual + " - ", é subgrupo
                    if proxima["nome"].startswith(nome_atual + " -") or proxima["nome"].startswith(nome_atual):
                        eh_cabecalho = True
                        break
                    # Se a próxima tem o mesmo valor mas nome diferente, é outra conta
                
                if not eh_cabecalho:
                    contas_folha.append(l)
            
            # Ordena por empenhado desc e pega top 10
            contas_folha.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = contas_folha[:10]
            
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

print("\n[OK] Lógica atualizada para extrair contas analíticas (linhas folha).")
