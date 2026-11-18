# -*- coding: utf-8 -*-
"""
Rota do BP (Balanço Patrimonial)
Criado em 18/11/2026, seguindo o padrão do DFC, DVP e DMPL.
"""
import csv
import os
import json
import traceback
from fastapi import APIRouter, Response
import psycopg2
from pc_backend.app.config import PG_CONFIG

router = APIRouter(prefix="/api/analise_bp", tags=["bp"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")


def limpar(v):
    if not v:
        return 0.0
    v = str(v).replace("R$", "").strip()
    if v in ["-", "0,00", ""]:
        return 0.0
    if v.endswith("C"):
        v = v[:-1]
    if v.endswith("D"):
        v = v[:-1]
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    try:
        return float(v)
    except Exception:
        return 0.0


def processar_bp(caminho):
    """
    Le o CSV do Balanco Patrimonial.
    Colunas 0-2: Ativo. Colunas 3-5: Passivo/PL.
    """
    dados = {
        "ativo_circulante": {"atual": 0.0, "anterior": 0.0},
        "ativo_nao_circulante": {"atual": 0.0, "anterior": 0.0},
        "ativo_total": {"atual": 0.0, "anterior": 0.0},
        "passivo_circulante": {"atual": 0.0, "anterior": 0.0},
        "passivo_nao_circulante": {"atual": 0.0, "anterior": 0.0},
        "passivo_total": {"atual": 0.0, "anterior": 0.0},
        "patrimonio_liquido": {"atual": 0.0, "anterior": 0.0},
        "linhas": [],
    }
    
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    
    for linha in linhas:
        if not linha:
            continue
        
        cols = [c.strip() for c in linha]
        
        # Ativo (colunas 0-2)
        if len(cols) >= 3:
            nome_ativo = cols[0].upper()
            val_ativo = limpar(cols[1])
            val_ativo_ant = limpar(cols[2])
            
            if nome_ativo == "ATIVO CIRCULANTE":
                dados["ativo_circulante"]["atual"] = val_ativo
                dados["ativo_circulante"]["anterior"] = val_ativo_ant
            elif nome_ativo == "ATIVO NÃO CIRCULANTE":
                dados["ativo_nao_circulante"]["atual"] = val_ativo
                dados["ativo_nao_circulante"]["anterior"] = val_ativo_ant
        
        # Passivo (colunas 3-5)
        if len(cols) >= 6:
            nome_passivo = cols[3].upper()
            val_passivo = limpar(cols[4])
            val_passivo_ant = limpar(cols[5])
            
            if nome_passivo == "PASSIVO CIRCULANTE":
                dados["passivo_circulante"]["atual"] = val_passivo
                dados["passivo_circulante"]["anterior"] = val_passivo_ant
            elif "PASSIVO NAO-CIRCULANTE" in nome_passivo or "PASSIVO NÃO CIRCULANTE" in nome_passivo:
                dados["passivo_nao_circulante"]["atual"] = val_passivo
                dados["passivo_nao_circulante"]["anterior"] = val_passivo_ant
            elif "TOTAL DO PASSIVO" in nome_passivo:
                dados["passivo_total"]["atual"] = val_passivo
                dados["passivo_total"]["anterior"] = val_passivo_ant
            elif "PATRIMÔNIO LÍQUIDO" in nome_passivo or "PATRIMONIO LIQUIDO" in nome_passivo:
                # Patrimônio Líquido é o total do passivo + PL
                dados["patrimonio_liquido"]["atual"] = val_passivo
                dados["patrimonio_liquido"]["anterior"] = val_passivo_ant
    
    # Ativo Total = Ativo Circulante + Ativo Não Circulante
    dados["ativo_total"]["atual"] = dados["ativo_circulante"]["atual"] + dados["ativo_nao_circulante"]["atual"]
    dados["ativo_total"]["anterior"] = dados["ativo_circulante"]["anterior"] + dados["ativo_nao_circulante"]["anterior"]
    
    # Passivo Total = Passivo Circulante + Passivo Não Circulante
    if dados["passivo_total"]["atual"] == 0:
        dados["passivo_total"]["atual"] = dados["passivo_circulante"]["atual"] + dados["passivo_nao_circulante"]["atual"]
    if dados["passivo_total"]["anterior"] == 0:
        dados["passivo_total"]["anterior"] = dados["passivo_circulante"]["anterior"] + dados["passivo_nao_circulante"]["anterior"]
    
    # PL = Ativo Total - Passivo Total
    dados["patrimonio_liquido"]["atual"] = dados["ativo_total"]["atual"] - dados["passivo_total"]["atual"]
    dados["patrimonio_liquido"]["anterior"] = dados["ativo_total"]["anterior"] - dados["passivo_total"]["anterior"]

    # === Aliases para compatibilidade com o frontend (analise_bp.html) ===
    dados["total_ativo"]  = dict(dados["ativo_total"])
    dados["total_passivo"] = dict(dados["passivo_total"])

    # === Campos derivados de linhas[] para o render do frontend ===
    # Mapeia nomes do CSV para chaves que o front espera
    _mapa = {
        "caixa":             ["CAIXA E EQUIVALENTES DE CAIXA", "CAIXA E EQUIVALENTES"],
        "creditos":          ["CRÉDITOS A CURTO PRAZO", "CREDITOS A CURTO PRAZO"],
        "ativo_realizavel":  ["ATIVO REALIZÁVEL A LONGO PRAZO", "ATIVO REALIZAVEL A LONGO PRAZO"],
        "imobilizado":       ["IMOBILIZADO", "IMOBILIZADO "],
    }
    for chave, nomes in _mapa.items():
        dados[chave] = {"atual": 0.0, "anterior": 0.0}
        for linha_item in dados["linhas"]:
            nome_ativo = (linha_item.get("ativo") or "").strip().upper()
            if nome_ativo in [n.upper() for n in nomes]:
                dados[chave]["atual"]    = linha_item.get("ativo_atual", 0.0) or 0.0
                dados[chave]["anterior"] = linha_item.get("ativo_anterior", 0.0) or 0.0
                break

    
    # Guarda as linhas brutas para renderização
    for linha in linhas:
        if linha and len(linha) >= 6:
            dados["linhas"].append({
                "ativo": linha[0].strip(),
                "ativo_atual": limpar(linha[1]),
                "ativo_anterior": limpar(linha[2]),
                "passivo": linha[3].strip(),
                "passivo_atual": limpar(linha[4]),
                "passivo_anterior": limpar(linha[5]),
            })
    
    return {"dados": dados}


@router.get("/historico")
def get_historico_bp():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[BP] Erro ao listar historico: {e}")
        return []


@router.get("/historico/{id}")
def get_historico_bp_id(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_bp WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.get("/{periodo}")
def api_analise_bp(periodo: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"erro": "faltando", "mensagem": f"CSV nao encontrado: BALANCO_PATRIMONIAL_{p_limpo}.csv"}
        return processar_bp(caminho)
    except Exception as e:
        print(f"[BP] ERRO: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}


@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_bp(periodo: str, periodo_anterior: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"ok": False, "mensagem": f"CSV nao encontrado: BALANCO_PATRIMONIAL_{p_limpo}.csv"}
        
        resultado = processar_bp(caminho)
        if resultado.get("erro"):
            return {"ok": False, "mensagem": resultado.get("mensagem", "Erro no processamento")}
        
        dados_json = resultado["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historico_analise_bp (periodo, data_geracao, resultado_json)
            VALUES (%s, NOW(), %s) RETURNING id
        """, (periodo_label, json.dumps(dados_json, ensure_ascii=False)))
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[BP] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.delete("/excluir/{id}")
def excluir_bp(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_bp WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_bp(id: int):
    try:
        from playwright.sync_api import sync_playwright
        import time
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_bp WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)
        
        url = "http://127.0.0.1:994/analise_bp?id=" + str(id) + "&_t=" + str(int(time.time()))
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.add_style_tag(content="button, select, .top-bar, .filtros, .sidebar { display: none !important; }")
            page.wait_for_timeout(1000)
            pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"})
            browser.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Analise_BP_{id}.pdf"},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[BP] ERRO NO PDF: {e}\n{tb}")
        return Response(content=f"ERRO: {e}\n\n{tb}".encode("utf-8"), media_type="text/plain", status_code=500)

