c = open('main.py', encoding='utf-8-sig').read()

if 'def api_comparativo_receitas_v2' not in c:
    nova_rota = r'''
@app.get("/api/comparativo_receitas_v2/{periodo_atual}")
def api_comparativo_receitas_v2(periodo_atual: str):
    import os, re
    
    upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
    
    # Calcula o período anterior (mesmo trimestre do ano anterior)
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
    
    def parse_valor(s):
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try:
            return float(s)
        except:
            return 0.0
    
    def parse_pct(s):
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try:
            return float(s)
        except:
            return 0.0
    
    def ler_csv(periodo):
        if not periodo:
            return None
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_RECEITAS_{periodo_formatado}.csv")
        
        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_RECEITAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
        
        if not os.path.exists(arquivo):
            return None
        
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            
            dados = {
                "orcado_total": 0.0,
                "realizado_total": 0.0,
                "percentual_total": 0.0,
                "grupos": [],
                "cores": []
            }
            
            grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERÊNCIAS CORRENTES", "RECEITAS DE SERVIÇOS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIÇÕES"]
            
            for linha in linhas:
                if ";" not in linha:
                    continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4:
                    continue
                
                nome = partes_linha[0].strip().strip('"')
                if not nome:
                    continue
                
                if nome == "RECEITA REALIZADA":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["realizado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])
                
                elif nome in grupos_nomes:
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })
                
                elif nome.upper().startswith("COREN "):
                    dados["cores"].append({
                        "nome": nome.replace("COREN ", "").strip(),
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })
            
            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV {arquivo}: {e}")
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
        "anterior": anterior or {"orcado_total": 0, "realizado_total": 0, "percentual_total": 0, "grupos": [], "cores": []}
    }
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota /api/comparativo_receitas_v2 criada!")
else:
    print("[AVISO] Rota já existe.")
