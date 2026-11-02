c = open('main.py', encoding='utf-8-sig').read()

# Verifica se a rota /upload já foi alterada para processar o Centro de Custos
if "Centro de Custos" not in c or "processar_centro_custos" not in c:
    # Substitui a rota /upload por uma versão que processa o Centro de Custos
    rota_antiga = """@app.post("/upload")
async def upload_arquivo(file: UploadFile = File(...)):
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as b: shutil.copyfileobj(file.file, b)
    return {"filename": file.filename, "status": "sucesso"}"""
    
    rota_nova = """@app.post("/upload")
async def upload_arquivo(file: UploadFile = File(...), tipo_relatorio: str = Form(None)):
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as b: shutil.copyfileobj(file.file, b)
    
    # Se for Centro de Custos, processa o CSV e retorna os dados
    if tipo_relatorio == "Centro de Custos":
        import csv, io
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                decoded = f.read()
            reader = csv.DictReader(io.StringIO(decoded))
            centros = []
            for row in reader:
                nome = row.get("Centro de Custo") or row.get("centro_custo") or row.get("Nome") or row.get("nome") or ""
                valor_str = row.get("Valor") or row.get("valor") or row.get("Valor (R$)") or "0"
                valor_str = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    valor = float(valor_str)
                except:
                    valor = 0.0
                if nome.strip():
                    centros.append({"nome": nome.strip(), "valor": valor})
            return {"filename": file.filename, "status": "sucesso", "dados_processados": centros}
        except Exception as e:
            return {"filename": file.filename, "status": "sucesso", "erro_processamento": str(e)}
    
    return {"filename": file.filename, "status": "sucesso"}"""
    
    if rota_antiga in c:
        c = c.replace(rota_antiga, rota_nova)
        print("[OK] Rota /upload agora processa Centro de Custos!")
    else:
        print("[ERRO] Rota /upload não encontrada no formato esperado.")
        # Tenta encontrar e substituir de forma mais flexível
        import re
        padrao = r'@app\.post\("/upload"\)\s*async def upload_arquivo\(file: UploadFile = File\(\.\.\.\)\):\s*.*?return \{"filename": file\.filename, "status": "sucesso"\}'
        if re.search(padrao, c, re.DOTALL):
            c = re.sub(padrao, rota_nova, c, flags=re.DOTALL)
            print("[OK] Rota /upload substituída via regex!")
        else:
            print("[ERRO] Não foi possível substituir a rota.")
    
    # Adicionar o import do Form
    if "from fastapi import" in c and "Form" not in c:
        c = c.replace("from fastapi import", "from fastapi import Form,")
    elif "from fastapi import" not in c:
        c = "from fastapi import Form\n" + c
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] main.py atualizado!")
else:
    print("[AVISO] A rota já foi alterada.")
