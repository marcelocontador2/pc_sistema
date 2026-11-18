# -*- coding: utf-8 -*-
"""
Rota do DMPL (Demonstração das Mutações do Patrimônio Líquido)
Criado em 18/11/2026, seguindo o padrão do DFC e DVP.
"""
import csv
import os
import json
import traceback
from fastapi import APIRouter, Response
import psycopg2
from pc_backend.app.config import PG_CONFIG

router = APIRouter(prefix="/api/analise_dmpl", tags=["dmpl"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")


def limpar(v):
    if not v:
        return 0.0
    v = str(v).replace("R$", "").strip()
    if v in ["-", "0,00", ""]:
        return 0.0
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    try:
        return float(v)
    except Exception:
        return 0.0



def processar_dmpl(caminho):
    """
    Le o CSV do DMPL.
    Filtra apenas as linhas relevantes (Saldos, Ajustes, Resultado, etc.)
    e corrige o encoding.
    """
    dados = {
        "saldos_iniciais": {"atual": 0.0, "anterior": 0.0},
        "ajustes_exercicios": {"atual": 0.0, "anterior": 0.0},
        "aumento_capital": {"atual": 0.0, "anterior": 0.0},
        "resultado_exercicio": {"atual": 0.0, "anterior": 0.0},
        "resultado_periodo": {"atual": 0.0, "anterior": 0.0},
        "ajustes_avaliacao": {"atual": 0.0, "anterior": 0.0},
        "constituicao_reservas": {"atual": 0.0, "anterior": 0.0},
        "demais_variacoes": {"atual": 0.0, "anterior": 0.0},
        "saldos_finais": {"atual": 0.0, "anterior": 0.0},
        "linhas": [],
    }
    
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    
    # Palavras-chave das linhas relevantes
    palavras_chave = [
        "SALDOS INICIAIS", "AJUSTES DE EXERC", "AUMENTO DE CAPITAL",
        "RESULTADO DO EXERC", "RESULTADO DO PER", "AJUSTES DE AVALIA",
        "CONSTITUI", "DEMAIS VARIA", "SALDOS FINAIS"
    ]
    
    def corrigir_encoding(texto):
        try:
            # Tenta corrigir o encoding (latin-1 -> utf-8)
            return texto.encode("latin-1").decode("utf-8", errors="ignore")
        except Exception:
            return texto
    
    for linha in linhas:
        if not linha or len(linha) < 9:
            continue
        
        descricao_original = linha[0].strip()
        descricao_corrigida = corrigir_encoding(descricao_original).upper()
        
        # Verifica se a linha é relevante
        is_relevante = any(p in descricao_corrigida for p in palavras_chave)
        if not is_relevante:
            continue
        
        val_total = limpar(linha[8]) if len(linha) > 8 else 0.0
        val_acum = limpar(linha[7]) if len(linha) > 7 else 0.0
        
        # Preenche os campos específicos
        if "SALDOS INICIAIS" in descricao_corrigida:
            dados["saldos_iniciais"]["atual"] = val_acum
            dados["saldos_iniciais"]["anterior"] = val_total
        elif "AJUSTES DE EXERC" in descricao_corrigida:
            dados["ajustes_exercicios"]["atual"] = val_acum
            dados["ajustes_exercicios"]["anterior"] = val_total
        elif "AUMENTO DE CAPITAL" in descricao_corrigida:
            dados["aumento_capital"]["atual"] = val_acum
            dados["aumento_capital"]["anterior"] = val_total
        elif "RESULTADO DO EXERC" in descricao_corrigida:
            dados["resultado_exercicio"]["atual"] = val_acum
            dados["resultado_exercicio"]["anterior"] = val_total
        elif "RESULTADO DO PER" in descricao_corrigida:
            dados["resultado_periodo"]["atual"] = val_acum
            dados["resultado_periodo"]["anterior"] = val_total
        elif "AJUSTES DE AVALIA" in descricao_corrigida:
            dados["ajustes_avaliacao"]["atual"] = val_acum
            dados["ajustes_avaliacao"]["anterior"] = val_total
        elif "CONSTITUI" in descricao_corrigida and "RESERVAS" in descricao_corrigida:
            dados["constituicao_reservas"]["atual"] = val_acum
            dados["constituicao_reservas"]["anterior"] = val_total
        elif "DEMAIS VARIA" in descricao_corrigida:
            dados["demais_variacoes"]["atual"] = val_acum
            dados["demais_variacoes"]["anterior"] = val_total
        elif "SALDOS FINAIS" in descricao_corrigida:
            dados["saldos_finais"]["atual"] = val_acum
            dados["saldos_finais"]["anterior"] = val_total
        
        # Adiciona a linha (apenas as relevantes)
        dados["linhas"].append({
            "descricao": descricao_corrigida,
            "valores": [limpar(c) for c in linha[1:9]],
        })
    
    return {"dados": dados}


@router.get("/{periodo}")
def api_analise_dmpl(periodo: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"DMPL_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"erro": "faltando", "mensagem": f"CSV nao encontrado: DMPL_{p_limpo}.csv"}
        return processar_dmpl(caminho)
    except Exception as e:
        print(f"[DMPL] ERRO: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}


@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_dmpl(periodo: str, periodo_anterior: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"DMPL_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"ok": False, "mensagem": f"CSV nao encontrado: DMPL_{p_limpo}.csv"}
        
        resultado = processar_dmpl(caminho)
        if resultado.get("erro"):
            return {"ok": False, "mensagem": resultado.get("mensagem", "Erro no processamento")}
        
        dados_json = resultado["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historico_analise_dmpl (periodo, data_geracao, resultado_json)
            VALUES (%s, NOW(), %s) RETURNING id
        """, (periodo_label, json.dumps(dados_json, ensure_ascii=False)))
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[DMPL] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico")
def get_historico_dmpl():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dmpl ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[DMPL] Erro ao listar historico: {e}")
        return []


@router.get("/historico/{id}")
def get_historico_dmpl_id(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dmpl WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.delete("/excluir/{id}")
def excluir_dmpl(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_dmpl WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_dmpl(id: int):
    try:
        from playwright.sync_api import sync_playwright
        import time
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dmpl WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)
        
        url = "http://127.0.0.1:994/analise_dmpl?id=" + str(id) + "&_t=" + str(int(time.time()))
        
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
            headers={"Content-Disposition": f"inline; filename=Analise_DMPL_{id}.pdf"},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[DMPL] ERRO NO PDF: {e}\n{tb}")
        return Response(content=f"ERRO: {e}\n\n{tb}".encode("utf-8"), media_type="text/plain", status_code=500)
