# -*- coding: utf-8 -*-
"""
Rotas de Análise de Liquidez.
Extraído do main.py para refatoração.
"""

import os
import json
import datetime
import sqlite3
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "pc_storage", "banco_dados.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

# =========================================================
# FUNÇÃO AUXILIAR
# =========================================================
def _calc_liquidez(periodo):
    """Calcula indices de liquidez/estrutura para exercicio ATUAL e ANTERIOR."""
    from pc_backend.matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
    caminho_bp = _get_csv("BALANCO_PATRIMONIAL", periodo)
    if not caminho_bp:
        return None
    l_bp = _ler_linhas(caminho_bp)

    def _norm(s):
        import unicodedata
        s = unicodedata.normalize("NFKD", str(s))
        return "".join(c for c in s if not unicodedata.combining(c)).upper().strip()

    def buscar(*termos):
        for termo in termos:
            termo_norm = _norm(termo)
            for p in l_bp:
                for col_espec in (0, 3):
                    if len(p) > col_espec and termo_norm in _norm(p[col_espec]):
                        col_atual = col_espec + 1
                        col_ant = col_espec + 2
                        v_atual = v_ant = 0.0
                        if len(p) > col_atual:
                            try:
                                v_atual = abs(_limpar_valor(p[col_atual]))
                            except Exception:
                                pass
                        if len(p) > col_ant:
                            try:
                                v_ant = abs(_limpar_valor(p[col_ant]))
                            except Exception:
                                pass
                        if v_atual > 0 or v_ant > 0:
                            return v_atual, v_ant
        return 0.0, 0.0

    caixa_a, caixa_p = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ac_a, ac_p = buscar("ATIVO CIRCULANTE")
    est_a, est_p = buscar("ESTOQUES")
    rlp_a, rlp_p = buscar("ATIVO REALIZAVEL A LONGO PRAZO", "REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO")
    anc_a, anc_p = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE")
    imob_a, imob_p = buscar("IMOBILIZADO", "IMOBILIZADO LIQUIDO")
    pc_a, pc_p = buscar("PASSIVO CIRCULANTE")
    pnc_a, pnc_p = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE")
    pt_a, pt_p = buscar("TOTAL DO PASSIVO", "PASSIVO TOTAL", "TOTAL PASSIVO")
    at_a, at_p = buscar("ATIVO TOTAL", "TOTAL DO ATIVO", "TOTAL ATIVO")
    pl_a, pl_p = buscar("TOTAL DO PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO", "PATRIMONIO SOCIAL")

    def _bloco(caixa, ac, est, rlp, anc, imob, pc, pnc, pt, at, pl):
        if not anc and imob:
            anc = imob
        if not pt and pc and pnc:
            pt = pc + pnc
        if not at:
            if ac and anc:
                at = ac + anc
            elif ac:
                at = ac + (rlp or 0.0) + (imob or 0.0)
        if not at and pt and pl:
            at = pt + pl
        if not pl and at and pt:
            pl = at - pt
        if at and pt and pl:
            soma = pt + pl
            if abs(at - soma) > 1.0:
                at = soma
        return dict(caixa=caixa, ac=ac, est=est, rlp=rlp, anc=anc, imob=imob,
                    pc=pc, pnc=pnc, pt=pt, at=at, pl=pl)

    b_atual = _bloco(caixa_a, ac_a, est_a, rlp_a, anc_a, imob_a, pc_a, pnc_a, pt_a, at_a, pl_a)
    b_ant   = _bloco(caixa_p, ac_p, est_p, rlp_p, anc_p, imob_p, pc_p, pnc_p, pt_p, at_p, pl_p)

    def div(a, b):
        return (a / b) if b else 0.0

    def pct(a, b):
        return ((a / b) * 100) if b else 0.0

    def fmt(v):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _indices(b):
        return {
            "liquidez": {
                "liquidez_imediata": fmt(div(b["caixa"], b["pc"])),
                "liquidez_corrente": fmt(div(b["ac"], b["pc"])),
                "liquidez_seca": fmt(div(b["ac"] - b["est"], b["pc"])),
                "liquidez_geral": fmt(div(b["ac"] + b["rlp"], b["pc"] + b["pnc"])),
            },
            "estrutura": {
                "endividamento_geral": fmt(pct(b["pt"], b["at"])),
                "part_capital_terceiros": fmt(pct(b["pt"], b["pl"])),
                "imobilizacao_pl": fmt(pct(b["imob"], b["pl"])),
            },
            "valores": {
                "caixa": b["caixa"],
                "ativo_circulante": b["ac"],
                "estoques": b["est"],
                "realizavel_lp": b["rlp"],
                "ativo_nao_circulante": b["anc"],
                "imobilizado": b["imob"],
                "passivo_circulante": b["pc"],
                "passivo_nao_circulante": b["pnc"],
                "passivo_total": b["pt"],
                "ativo_total": b["at"],
                "patrimonio_liquido": b["pl"],
            },
        }

    idx_atual = _indices(b_atual)
    idx_ant = _indices(b_ant)

    periodo_anterior_label = None
    for p in l_bp[:12]:
        linha = ";".join(str(c) for c in p)
        if "PERIODO ANTERIOR" in _norm(linha):
            import re as _re
            m2 = _re.search(r"(\d{2}/\d{2}/(\d{4}))\s*a\s*(\d{2}/\d{2}/(\d{4}))", linha)
            if m2:
                periodo_anterior_label = f"{m2.group(2)} - TRIMESTRE 3"
            break

    return {
        "periodo": periodo,
        "periodo_anterior": periodo_anterior_label or "Exercí­cio Anterior",
        "liquidez": idx_atual["liquidez"],
        "estrutura": idx_atual["estrutura"],
        "valores": idx_atual["valores"],
        "liquidez_anterior": idx_ant["liquidez"],
        "estrutura_anterior": idx_ant["estrutura"],
        "valores_anterior": idx_ant["valores"],
    }
@router.get("/liquidez")
async def serve_liquidez():
    caminho = os.path.join(FRONTEND_DIR, "liquidez.html")
    return FileResponse(caminho)


@router.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str):
    dados = _calc_liquidez(periodo)
    if not dados:
        return {"erro": True, "mensagem": "Balanco Patrimonial nao encontrado para este periodo."}
    return dados


@router.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez_rota(periodo: str):
    try:
        dados = _calc_liquidez(periodo)
        if not dados:
            return {"erro": True, "mensagem": "Sem dados para salvar."}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Liquidez salva com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.get("/historico_liquidez")
def listar_historico_liquidez():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_liquidez ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    resultado = []
    for r in rows:
        resultado.append({
            "id": r[0],
            "periodo": r[1],
            "data_geracao": r[2],
            "dados": r[3]
        })
    return Response(content=json.dumps(resultado), media_type="application/json")


@router.get("/historico_liquidez/{id}")
async def get_liquidez_id(id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    dados = json.loads(row[2])
    dados["_periodo_hist"] = row[0]
    dados["_data_hist"] = row[1]
    return dados


@router.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_liquidez WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/gerar_pdf_liquidez/{id}")
def gerar_pdf_liquidez(id: int):
    return Response(content="PDF em desenvolvimento", media_type="text/plain")
