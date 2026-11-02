c = open('main.py', encoding='utf-8-sig').read()

if "def importar_centro_custos" not in c:
    nova_rota = r'''
@app.post("/api/centro_custos/importar")
async def importar_centro_custos(file: UploadFile = File(...)):
    import csv, io
    try:
        # Lê o conteúdo do arquivo
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # Remove BOM se houver
        reader = csv.DictReader(io.StringIO(decoded))
        
        centros = []
        for row in reader:
            # Tenta encontrar as colunas (aceita variações de nome)
            nome = row.get("Centro de Custo") or row.get("centro_custo") or row.get("Nome") or row.get("nome") or ""
            valor_str = row.get("Valor") or row.get("valor") or row.get("Valor (R$)") or "0"
            
            # Limpa o valor (troca vírgula por ponto e remove R$)
            valor_str = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                valor = float(valor_str)
            except:
                valor = 0.0
            
            if nome.strip():
                centros.append({"nome": nome.strip(), "valor": valor})
        
        return {"erro": False, "centros": centros}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    
    # Garantir que o UploadFile e File estão importados
    if "from fastapi import" in c and "UploadFile" not in c:
        c = c.replace("from fastapi import", "from fastapi import UploadFile, File,")
    elif "from fastapi import" not in c:
        c = "from fastapi import UploadFile, File\n" + c
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota de importação de CSV do Centro de Custos adicionada!")
else:
    print("[AVISO] A rota de importação já existe.")
