import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Remove completamente a função antiga (do @app.get até o próximo @app ou def)
inicio = c.find('@app.get("/api/centro_custos/{periodo}")')
if inicio != -1:
    # Encontra o próximo @app ou def após o início
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio + 10)
        if pos != -1 and pos < fim:
            fim = pos
    
    # Remove o bloco antigo
    c = c[:inicio] + c[fim:]
    print("[OK] Bloco antigo removido!")

# 2. Adiciona a nova função limpa (antes do if __name__)
nova_funcao = '''
@app.get("/api/centro_custos/{periodo}")
def api_centro_custos(periodo: str):
    import os, csv, io
    
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    periodo_formatado = periodo.replace("-", "_")
    arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")
    
    if not os.path.exists(arquivo):
        for f in os.listdir(upload_dir):
            if periodo_formatado in f:
                arquivo = os.path.join(upload_dir, f)
                break
    
    if not os.path.exists(arquivo):
        return {"erro": True, "mensagem": f"Arquivo para o período {periodo} não encontrado."}
    
    try:
        try:
            with open(arquivo, "r", encoding="utf-8-sig") as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin-1") as f:
                linhas = f.readlines()
        
        inicio_dados = 0
        for i, linha in enumerate(linhas):
            if "Centro de Custo x Conta" in linha:
                inicio_dados = i + 1
                break
        
        if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
            inicio_dados += 1
        
        centros = []
        for linha in linhas[inicio_dados:]:
            if ";" in linha:
                partes = linha.strip().split(";")
            else:
                partes = linha.strip().split(",")
            
            if len(partes) < 2:
                continue
            
            nome = partes[0].strip().strip('"')
            if not nome or "TOTAL" in nome.upper() or "Centro de Custo" in nome:
                continue
            
            valor = 0.0
            for parte in reversed(partes):
                parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                try:
                    valor = float(parte_limpa)
                    if valor > 0:
                        break
                except:
                    continue
            
            centros.append({"nome": nome, "valor": valor})
        
        return {"erro": False, "periodo": periodo, "centros": centros}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''

if 'if __name__ == "__main__":' in c:
    c = c.replace('if __name__ == "__main__":', nova_funcao + '\nif __name__ == "__main__":')
else:
    c += "\n" + nova_funcao

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Nova função api_centro_custos adicionada!")
