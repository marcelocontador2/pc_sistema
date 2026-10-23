import os
import glob
import re
from fastapi import HTTPException

@app.get("/periodos_importados/{tipo_relatorio}")
async def get_periodos_importados(tipo_relatorio: str):
    periodos = []
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    if os.path.exists(pasta):
        arquivos = glob.glob(os.path.join(pasta, "*.csv"))
        for arq in arquivos:
            nome = os.path.basename(arq).upper()
            if tipo_relatorio.upper() in nome or ("PATRIMONIAL" in tipo_relatorio.upper() and "BALANCO" in nome):
                partes = os.path.basename(arq).replace(".csv", "").split("_")
                
                ano = 2026
                p_tipo = "TRIMESTRE"
                p_valor = "1"
                
                for i, p in enumerate(partes):
                    if len(p) == 4 and p.isdigit():
                        ano = int(p)
                        if i + 2 < len(partes):
                            p_tipo = partes[i+1]
                            p_valor = partes[i+2]
                        break
                
                label = f"{ano} - {p_tipo} {p_valor}"
                valor = f"{ano}-{p_tipo}-{p_valor}"
                periodos.append({"ano": ano, "periodo": label, "label": label, "valor": valor})
                
    unicos = list({v['label']:v for v in periodos}.values())
    return sorted(unicos, key=lambda x: x["ano"], reverse=True)

@app.get("/analise_cruzada/{periodo}")
async def analise_cruzada(periodo: str):
    try:
        p_limpo = re.sub(r'[^A-Z0-9]', '_', periodo.upper())
        p_limpo = re.sub(r'_+', '_', p_limpo).strip('_')
        
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        path_bp = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
        
        if not os.path.exists(path_bp):
            return {"erro": f"Arquivo {os.path.basename(path_bp)} nao encontrado", "ativo_total": 0, "passivo_pl": 0, "diferenca": 0, "status": "ERRO"}

        ativo = 0.0
        passivo = 0.0

        with open(path_bp, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for linha in f:
                partes = linha.split(';')
                if len(partes) >= 4:
                    col0 = partes[0].strip().replace('"', '').upper()
                    col2 = partes[2].strip().replace('"', '').upper()
                    
                    if col0 == "TOTAL":
                        ativo = _limpar_valor(partes[1])
                    if col2 == "TOTAL":
                        passivo = _limpar_valor(partes[3])

        diferenca = ativo - passivo
        status = "OK" if abs(diferenca) < 0.05 else "ERRO"
        
        return {
            "ativo_total": ativo,
            "passivo_pl": passivo,
            "diferenca": diferenca,
            "status": status
        }
    except Exception as e:
        return {"erro": str(e), "ativo_total": 0, "passivo_pl": 0, "diferenca": 0, "status": "ERRO"}

# Injeta a importação no final do main para registrar as rotas
import sys
import importlib