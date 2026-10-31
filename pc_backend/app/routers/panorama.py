"""
Rota do Panorama — versão final (31/10/2026).
Calcula Ativo, Passivo, PL, Receitas, Despesas, Superávit Orçamentário,
Superávit Patrimonial (DVP) e Superávit Financeiro (BP).
"""
import json
import os
import sqlite3
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fpdf import FPDF
from fpdf.enums import XPos, YPos
try:
    from matriz_integridade import _limpar_valor
except ImportError:
    def _limpar_valor(v):
        if v is None:
            return 0.0
        s = str(v).strip().replace(".", "").replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return 0.0
router = APIRouter(prefix="/api/panorama", tags=["panorama"])
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "pc_storage", "banco_dados.db"
)
def buscar_valor(linhas, termo, coluna):
    termo = termo.upper().strip()
    for linha in linhas:
        if len(linha) > coluna and termo in str(linha[0]).upper():
            try:
                return abs(_limpar_valor(linha[coluna]))
            except Exception:
                return 0.0
    return 0.0
def calcular_bp(linhas_bp):
    ativo_total = 0.0
    passivo_total = 0.0
    pl = 0.0
    for linha in linhas_bp:
        if len(linha) < 4:
            continue
        col0 = str(linha[0]).upper().strip()
        col2 = str(linha[2]).upper().strip()
        try:
            v1 = abs(_limpar_valor(linha[1])) if len(linha) > 1 else 0.0
            v3 = abs(_limpar_valor(linha[3])) if len(linha) > 3 else 0.0
        except Exception:
            continue
        if col0 == "TOTAL" and v1 > ativo_total:
            ativo_total = v1
        if "TOTAL DO PASSIVO" in col2:
            passivo_total = v3
        if "TOTAL DO PATRIM" in col2 and "QUIDO" in col2:
            pl = v3
    if pl == 0.0:
        pl = ativo_total - passivo_total
    return {
        "ativo_total": ativo_total,
        "passivo_total": passivo_total,
        "patrimonio_liquido": pl,
    }
def calcular_bo(linhas_bo):
    receita = 0.0
    despesa = 0.0
    for linha in linhas_bo:
        if len(linha) > 6:
            col0 = str(linha[0]).upper().strip()
            if "SUB-TOTAL DAS RECEITAS" in col0 or "SUB-TOTAL DAS RECEITA" in col0:
                try:
                    receita = abs(_limpar_valor(linha[6]))
                except Exception:
                    pass
                break
    for linha in linhas_bo:
        if len(linha) > 6:
            col0 = str(linha[0]).upper().strip().rstrip(":")
            if col0 == "TOTAL":
                try:
                    v = abs(_limpar_valor(linha[6]))
                    if v > despesa:
                        despesa = v
                except Exception:
                    pass
    return {"receita_realizada": receita, "despesa_empenhada": despesa}
def calcular_dvp(linhas_dvp):
    """Calcula o superavit/deficit patrimonial do DVP.
    O valor esta na linha 49 (RESULTADO PATRIMONIAL) e linhas seguintes."""
    for i, linha in enumerate(linhas_dvp):
        col0 = str(linha[0]).upper().strip() if len(linha) > 0 else ""
        if "RESULTADO PATRIMONIAL" in col0:
            # O valor pode estar na propria linha ou nas seguintes
            # Tenta a propria linha primeiro
            for val in reversed(linha[1:]):
                if val and str(val).strip():
                    try:
                        return abs(_limpar_valor(val))
                    except Exception:
                        pass
            # Se nao achou, busca nas proximas 5 linhas
            for j in range(i + 1, min(i + 6, len(linhas_dvp))):
                for val in linhas_dvp[j]:
                    if val and str(val).strip():
                        try:
                            v = abs(_limpar_valor(val))
                            if v > 0:
                                return v
                        except Exception:
                            pass
    return 0.0
def calcular_superavit_financeiro(linhas_bp):
    """Calcula o superavit financeiro (Ativo Financeiro - Passivo Financeiro)."""
    ativo_fin = 0.0
    passivo_fin = 0.0
    superavit_direto = 0.0
    for linha in linhas_bp:
        if len(linha) < 2:
            continue
        col0 = str(linha[0]).upper().strip()
        col2 = str(linha[2]).upper().strip() if len(linha) > 2 else ""
        # Tenta pegar direto da linha "Superavit Financeiro"
        if "SUPERAVIT FINANCEIRO" in col0 or "SUPERAVIT/DEFICIT FINANCEIRO" in col0:
            for val in reversed(linha[1:]):
                if val and str(val).strip():
                    try:
                        v = abs(_limpar_valor(val))
                        if v > 0:
                            superavit_direto = v
                            break
                    except Exception:
                        pass
        # Calcula Ativo Financeiro - Passivo Financeiro
        if "ATIVO FINANCEIRO" in col0:
            try:
                if len(linha) > 1:
                    ativo_fin = abs(_limpar_valor(linha[1]))
            except Exception:
                pass
        if "PASSIVO FINANCEIRO" in col2:
            try:
                if len(linha) > 3:
                    passivo_fin = abs(_limpar_valor(linha[3]))
            except Exception:
                pass
    # Se achou o valor direto, usa; senao, calcula
    if superavit_direto > 0:
        return superavit_direto
    return ativo_fin - passivo_fin
def buscar_arquivo(periodo, tipo):
    nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?",
            (nome,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else []
    finally:
        conn.close()
@router.get("/{periodo}")
async def api_panorama(periodo: str):
    try:
        linhas_bp = buscar_arquivo(periodo, "BALANCO_PATRIMONIAL")
        if not linhas_bp:
            raise HTTPException(status_code=404, detail=f"Balanco Patrimonial nao encontrado para {periodo}")
        bp = calcular_bp(linhas_bp)
        caixa = buscar_valor(linhas_bp, "CAIXA E EQUIVALENTES", 1) or buscar_valor(linhas_bp, "CAIXA", 1)
        linhas_bo = buscar_arquivo(periodo, "BALANCO_ORCAMENTARIO")
        bo = calcular_bo(linhas_bo)
        superavit_orc = bo["receita_realizada"] - bo["despesa_empenhada"]
        linhas_dvp = buscar_arquivo(periodo, "DVP")
        superavit_patrimonial = calcular_dvp(linhas_dvp)
        superavit_financeiro = calcular_superavit_financeiro(linhas_bp)
        print(f"[PANORAMA] ativo={bp['ativo_total']}, passivo={bp['passivo_total']}, pl={bp['patrimonio_liquido']}")
        print(f"[PANORAMA] receita={bo['receita_realizada']}, despesa={bo['despesa_empenhada']}, superavit={superavit_orc}")
        print(f"[PANORAMA] superavit_patrimonial={superavit_patrimonial}, superavit_financeiro={superavit_financeiro}")
        return {
            "ativo_total": bp["ativo_total"],
            "passivo_total": bp["passivo_total"],
            "patrimonio_liquido": bp["patrimonio_liquido"],
            "caixa_bp": caixa,
            "receita_realizada": bo["receita_realizada"],
            "despesa_empenhada": bo["despesa_empenhada"],
            "superavit_orcamentario": superavit_orc,
            "superavit_patrimonial": superavit_patrimonial,
            "superavit_financeiro": superavit_financeiro,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PANORAMA] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/gerar_pdf_panorama_v2/{id}")
async def gerar_pdf_panorama(id: str):
    """Gera PDF do Panorama com visual moderno."""
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from fastapi.responses import Response
        if id.isdigit():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT periodo FROM historico_panorama WHERE id = ?", (int(id),))
            row = cursor.fetchone()
            conn.close()
            if not row:
                raise HTTPException(status_code=404, detail=f"Historico com ID {id} nao encontrado")
            periodo = row[0]
        else:
            periodo = id
        linhas_bp = buscar_arquivo(periodo, "BALANCO_PATRIMONIAL")
        if not linhas_bp:
            raise HTTPException(status_code=404, detail=f"Balanco Patrimonial nao encontrado para {periodo}")
        bp = calcular_bp(linhas_bp)
        caixa = buscar_valor(linhas_bp, "CAIXA E EQUIVALENTES", 1) or buscar_valor(linhas_bp, "CAIXA", 1)
        linhas_bo = buscar_arquivo(periodo, "BALANCO_ORCAMENTARIO")
        bo = calcular_bo(linhas_bo)
        superavit_orc = bo["receita_realizada"] - bo["despesa_empenhada"]
        linhas_dvp = buscar_arquivo(periodo, "DVP")
        superavit_patrimonial = calcular_dvp(linhas_dvp)
        superavit_financeiro = calcular_superavit_financeiro(linhas_bp)
        # PDF moderno
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)
        # Cabecalho azul escuro
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 8)
        pdf.cell(180, 10, "PANORAMA", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Resultados Gerais - {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Linha amarela de destaque
        pdf.set_draw_color(245, 180, 0)
        pdf.set_line_width(1.5)
        pdf.line(0, 35, 210, 35)
        # Funcao para formatar valor em milhoes
        def fmt_mi(v):
            try:
                s = f"R$ {v/1000000:,.1f} mi"
                return s.replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(v)
        cards = [
            ("Caixa e Equivalente de Caixa (BP)", caixa),
            ("Ativo Total", bp["ativo_total"]),
            ("Passivo Total", bp["passivo_total"]),
            ("Patrimonio Liquido", bp["patrimonio_liquido"]),
            ("Receitas Realizadas (BO)", bo["receita_realizada"]),
            ("Despesas Empenhadas (BO)", bo["despesa_empenhada"]),
            ("Superavit/Deficit Orcamentario", superavit_orc),
            ("Superavit Patrimonial (DVP)", superavit_patrimonial),
            ("Superavit Financeiro (BP)", superavit_financeiro),
        ]
        # Grid 3x3 de cards
        x_start = 15
        y_start = 48
        card_w = 55
        card_h = 32
        gap_x = 5
        gap_y = 8
        for i, (nome, valor) in enumerate(cards):
            col = i % 3
            lin = i // 3
            x = x_start + col * (card_w + gap_x)
            y = y_start + lin * (card_h + gap_y)
            # Fundo do card (azul claro)
            pdf.set_fill_color(233, 242, 250)
            pdf.rect(x, y, card_w, card_h, "F")
            # Valor em azul escuro
            pdf.set_text_color(0, 51, 102)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_xy(x + 2, y + 4)
            pdf.cell(card_w - 4, 8, fmt_mi(valor), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Label em cinza escuro
            pdf.set_text_color(80, 80, 80)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_xy(x + 2, y + 18)
            pdf.multi_cell(card_w - 4, 3.5, nome)
        # Rodape
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, 285, 195, 285)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_xy(15, 287)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        from datetime import datetime
        pdf.set_xy(135, 287)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")
        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=panorama_{periodo}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
