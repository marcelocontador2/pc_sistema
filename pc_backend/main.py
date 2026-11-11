# PATCH PG - troca sqlite3 por PostgreSQL (ver sqlite_compat.py)
import sqlite_compat

from fastapi.staticfiles import StaticFiles
from app.routers import dfc
from fastapi import Request, Request, FastAPI, Request
from historico_integridade import router as historico_router
from fastapi import FastAPI, UploadFile, File
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Response, Form
from fastapi.staticfiles import StaticFiles
from historico_integridade import router as historico_router
from fastapi.staticfiles import StaticFiles
import sqlite3
import shutil
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, shutil, io, glob, csv
import psycopg2
from app.core.database import DB_CONFIG
def _limpar_ascii(txt):
    """Limpa caracteres de controle, mantendo acentos (para fontes Unicode)."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
    s = s.replace("\\f", " ").replace("\\v", " ").replace("\\a", " ")
    s = s.replace(chr(12), " ").replace(chr(11), " ").replace(chr(7), " ")
    s = "".join(ch if (ord(ch) >= 32 and ord(ch) < 256) else " " for ch in s)
    return s

def _corrigir_encoding(txt):
    """Corrige encoding duplo (UTF-8 lido como latin-1)."""
    if not txt: return ""
    try:
        # Tenta decodificar como latin-1 e re-codificar como utf-8
        # Isso converte ç -> ç, ã -> ã, etc.
        s = txt.encode("latin-1", "ignore").decode("utf-8", "ignore")
        return s
    except:
        return txt


def _limpar_ascii(txt):
    """Limpa apenas tabulaçíµes e caracteres de controle, mantendo acentos."""
    if not txt: return ""
    s = str(txt)
    s = s.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    s = "".join(ch if ord(ch) >= 32 else " " for ch in s)
    return s


# import pandas as pd  # removido 31/10/2026 - nao usado
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
app = FastAPI(title="PC - Prestacao de Contas API")

# ===== MONKEY-PATCH PARA UTF-8 NO FPDF (v2) =====
import os as _os_mp
_FONT_PATH_UTF8 = "C:/Windows/Fonts/arial.ttf"

if _os_mp.path.exists(_FONT_PATH_UTF8):
    try:
        from fpdf import FPDF as _FPDF_Original

        _original_set_font = _FPDF_Original.set_font

        def _set_font_utf8(self, family="helvetica", style="", size=0):
            if str(family).lower() in ("helvetica", "arial"):
                try:
                    if "ArialUTF8" not in self.fonts:
                        self.add_font("ArialUTF8", "", _FONT_PATH_UTF8, uni=True)
                        self.add_font("ArialUTF8", "B", _FONT_PATH_UTF8, uni=True)
                        self.add_font("ArialUTF8", "I", _FONT_PATH_UTF8, uni=True)
                    family = "ArialUTF8"
                except Exception:
                    pass
            return _original_set_font(self, family, style, size)

        _FPDF_Original.set_font = _set_font_utf8
    except Exception as _e:
        print(f"[FPDF-UTF8] Erro no monkey-patch: {_e}")
# ===== FIM DO MONKEY-PATCH =====


@app.get("/dashboard_despesas")
def get_dashboard_despesas():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "dashboard_despesas.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": True, "mensagem": "Arquivo dashboard_despesas.html nao encontrado"}

@app.get("/configuracoes", response_class=HTMLResponse)
async def serve_configuracoes():
    import os
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "configuracoes.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
# === CONFIGURACOES GLOBAIS (31/10/2026) ===
@app.get("/api/configuracoes")
async def get_configuracoes():
    """Retorna as configuracoes globais (tipo_entidade: COFEN ou COREN)."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT chave, valor FROM configuracoes")
    rows = cur.fetchall()
    conn.close()
    return {k: v for k, v in rows}
@app.post("/api/configuracoes")
async def post_configuracoes(config: dict):
    """Salva as configuracoes globais. Ex: {"tipo_entidade": "COREN"}."""
    import sqlite3, os, datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for chave, valor in config.items():
        cur.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor, data_atualizacao) VALUES (?, ?, ?)",
            (chave, str(valor), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()
    return {"status": "ok", "configuracoes": config}
# Router novo do Panorama (31/10/2026)
# Servir arquivos estáticos da pasta pc_frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend")
if os.path.exists(frontend_path):
    app.mount("/pc_frontend", StaticFiles(directory=frontend_path), name="pc_frontend")
    print(f"âœ… Arquivos estáticos montados em: {frontend_path}")
from fastapi.responses import HTMLResponse
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "index.html"), encoding="utf-8") as f:
        return f.read()
@app.get("/analise")
async def obter_analise():
    return {"ativo_total": 616607030.65, "passivo_total": 12238786.04,
            "patrimonio_liquido": 604368244.61, "superavit_orcamentario": -70944403.02}
@app.get("/periodos")
async def obter_periodos():
    try:
        conn = psycopg2.connect(**DB_CONFIG); cur = conn.cursor()
        cur.execute("""

            SELECT DISTINCT p.ano, p.periodo_acumulado

            FROM periodo p

            JOIN documento_importado doc ON p.id = doc.periodo_id

            ORDER BY p.ano DESC, p.periodo_acumulado DESC

        """)
        rows = cur.fetchall(); cur.close(); conn.close()
        return [{"ano": r[0], "periodo": r[1], "label": f"{r[0]} - {r[1]}"} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro /periodos: {e}")
import glob
import glob
def _get_csv_por_tipo(tipo, periodo=None):
    import os, glob
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_uploads = os.path.join(base_dir, "..", "pc_storage", "uploads_raw")
    # Se o periodo foi informado (ex: 2026-MES-05), buscamos o arquivo exato
    if periodo and "-" in periodo:
        partes = periodo.split('-')
        ano = partes[0]
        tipo_p = partes[1]
        valor_p = partes[2]
        # Monta o nome padrao que salvamos no upload: BALANCETE_2026_MES_05.csv
        nome_arquivo = f"{tipo}_{ano}_{tipo_p}_{valor_p}.csv"
        caminho_exato = os.path.join(pasta_uploads, nome_arquivo)
        if os.path.exists(caminho_exato):
            return caminho_exato
    # Fallback (caso o periodo nao seja informado ou o arquivo nao exista)
    nomes_busca = [f"*{tipo.lower()}*.csv"]
    if os.path.exists(pasta_uploads):
        for padrao in nomes_busca:
            arquivos = glob.glob(os.path.join(pasta_uploads, padrao))
            if arquivos:
                return arquivos[0]
    return None
def _ler_csv_generico(filepath):
    dados = []
    with open(filepath, "r", encoding="latin-1") as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            clean = [str(c).replace('\n', ' ').replace('\r', ' ').strip() for c in row]
            dados.append(clean)
    return dados
def _buscar_dados(tipo, ano, periodo):
    if tipo.startswith("BALANCO") or tipo == "BALANCETE":
        return [{"grupo": "Demonstrativo", "valor": 0}]
    conn = psycopg2.connect(**DB_CONFIG); cur = conn.cursor()
    cur.execute(f"""
        SELECT b.codigo_conta, b.descricao_conta, b.saldo_atual, b.natureza_saldo
        FROM balancete_linha b
        JOIN documento_importado doc ON b.documento_id = doc.id
        JOIN periodo p ON doc.periodo_id = p.id
        WHERE p.ano = %s AND p.periodo_acumulado = %s
        ORDER BY b.codigo_conta
    """, (ano, periodo))
    rows = cur.fetchall(); cur.close(); conn.close()
    return [{"conta": r[0], "descricao": r[1], "valor": float(r[2]) if r[2] is not None else 0.0, "natureza": r[3] or ""} for r in rows]
@app.get("/demonstracoes/{tipo}")
async def obter_demonstracao(tipo: str, ano: int = Query(2026), periodo: str = Query("Jan-Set")):
    try:
        return _buscar_dados(tipo, ano, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro SQL: {str(e)}")
def _ler_csv(filepath, tipo=""):
    import re
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = _corrigir_encoding(f.read())
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados
    reader = csv.reader(io.StringIO(content), delimiter=';')
    for row in reader:
        clean_row = [str(c).replace('\n', ' ').replace('\r', ' ').replace('\ufeff', '').strip() for c in row]
        if not any(clean_row): continue
        # Garante 6 colunas
        max_cols = 6 if tipo != "BALANCO_ORCAMENTARIO" else 7
        clean_row = clean_row[:max_cols]
        while len(clean_row) < max_cols:
            clean_row.append('')
        dados.append(clean_row)
    return dados
# =======================================================
# CONFIGURAí‡íƒO DO BANCO DE DADOS SQLITE
# =======================================================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")


# === ROTA: Excluir relatorio CSV da pasta uploads_raw ===
@app.delete("/api/excluir_relatorio/{nome_arquivo}")
async def excluir_relatorio_csv(nome_arquivo: str):
    # Seguranca: impede path traversal
    if '..' in nome_arquivo or '/' in nome_arquivo or '\\' in nome_arquivo:
        raise HTTPException(status_code=400, detail="Nome de arquivo invalido.")
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado: " + nome_arquivo)
    try:
        os.remove(caminho)
        return {"ok": True, "mensagem": "Arquivo excluido: " + nome_arquivo}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao excluir: " + str(e))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''

        CREATE TABLE IF NOT EXISTS importacoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            tipo_relatorio TEXT NOT NULL,

            ano INTEGER NOT NULL,

            periodo_tipo TEXT NOT NULL,

            periodo_valor TEXT NOT NULL,

            nome_original TEXT NOT NULL,

            caminho_arquivo TEXT NOT NULL,

            data_importacao TEXT NOT NULL

        )

    ''')
    conn.commit()
    conn.close()
# Inicializa o banco na partida
init_db()
# =======================================================
# ROTA DE UPLOAD (IMPORTAí‡íƒO)
# =======================================================
from fastapi import File, UploadFile, Form
@app.get("/periodos_importados/{tipo_relatorio}")
async def get_periodos_importados(tipo_relatorio: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''

        SELECT DISTINCT ano, periodo_tipo, periodo_valor

        FROM importacoes

        WHERE tipo_relatorio = ?

        ORDER BY ano DESC, periodo_valor DESC

    ''', (tipo_relatorio,))
    resultados = cursor.fetchall()
    conn.close()
    periodos = []
    for r in resultados:
        periodos.append(f"{r[0]}-{r[1]}-{r[2]}")
    return {"periodos": periodos}
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path == "/" or request.url.path.endswith(".html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
app.add_middleware(NoCacheMiddleware)
@app.get("/download/pdf/{tipo}")
async def download_pdf(tipo: str, ano: int = Query(2026), periodo: str = Query("")):
    try:
        periodo_formatado = f"{ano}"
        if periodo and "-" in periodo:
            partes = periodo.split('-')
            tipo_p = partes[1]
            valor_p = partes[2]
            if tipo_p == "MES":
                meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                periodo_formatado = f"{meses[int(valor_p)]}/{ano}"
            elif tipo_p == "TRIMESTRE":
                periodo_formatado = f"{valor_p}Âº Tri/{ano}"
            else:
                periodo_formatado = f"Exercí­cio {ano}"
        csv_path = _get_csv_por_tipo(tipo, periodo)
        if not csv_path:
            raise HTTPException(status_code=404, detail=f"Arquivo CSV para {tipo} no perí­odo {periodo_formatado} não encontrado.")
        # Leitura robusta: tenta utf-8-sig, depois latin-1 (que aceita qualquer byte)
        content = ""
        for enc in ["latin-1", "utf-8-sig"]:
            try:
                with open(csv_path, "r", encoding=enc) as f:
                    content = _corrigir_encoding(f.read())
                break
            except:
                continue

        # Corrige caracteres corrompidos (ex: ç -> ç, ã -> ã)
        content = content.replace("íƒÂ§", "ç").replace("íƒÂ£", "ã").replace("íƒÂ¡", "á")
        content = content.replace("íƒÂ©", "é").replace("íƒ", "í­").replace("íƒÂ³", "í³")
        content = content.replace("íƒÂº", "íº").replace("íƒÂ¢", "í¢").replace("íƒÂª", "íª")
        content = content.replace("íƒÂ´", "í´").replace("íƒÂª", "íª").replace("íƒÂ§", "ç")
        content = content.replace("íƒÆ’", "íƒ").replace("íƒâ€°", "í‰").replace("íƒâ€œ", "í“")
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        fonte_padrao = "Helvetica"
        # Registra fonte Arial (regular, bold e italic)
        import os
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial.ttf")
        font_bold_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arialbd.ttf")
        font_italic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ariali.ttf")

        if os.path.exists(font_path):
            try:
                pdf.add_font("ArialUnicode", "", font_path, uni=True)
                if os.path.exists(font_bold_path):
                    pdf.add_font("ArialUnicode", "B", font_bold_path, uni=True)
                else:
                    pdf.add_font("ArialUnicode", "B", font_path, uni=True)
                if os.path.exists(font_italic_path):
                    pdf.add_font("ArialUnicode", "I", font_italic_path, uni=True)
                else:
                    pdf.add_font("ArialUnicode", "I", font_path, uni=True)
                fonte_padrao = "ArialUnicode"
                print("[INFO] Fonte Arial registrada com sucesso (regular, bold, italic)")
            except Exception as e:
                print(f"[AVISO] Erro ao registrar Arial: {e}")
                fonte_padrao = "Helvetica"
        else:
            fonte_padrao = "Helvetica"
            print("[AVISO] Fonte Arial nao encontrada, usando Helvetica")
        pdf.set_auto_page_break(auto=False)
        # ---------- LAYOUTS ----------
        if tipo == "BALANCETE":
            col_w   = [125, 0, 38, 38, 38, 38]
            headers = ["CONTA", "", "SALDO ANTERIOR", "DEBITOS", "CREDITOS", "SALDO"]
            titulo_pdf = "Balancete Contábil"
        elif tipo == "BALANCO_PATRIMONIAL":
            col_w   = [85, 30, 85, 30, 0, 0]
            headers = ["ESPECIFICACAO (ATIVO)", "Exercí­cio Atual", "ESPECIFICACAO (PASSIVO)", "Exercí­cio Atual", "", ""]
            titulo_pdf = "Balanço Patrimonial"
        elif tipo == "BALANCO_FINANCEIRO":
            col_w   = [68, 28, 28, 68, 28, 28]
            headers = ["ESPECIFICACAO (INGRESSOS)", "Exercí­cio Atual", "Exercí­cio Anterior", "ESPECIFICACAO (DISPENDIOS)", "Exercí­cio Atual", "Exercí­cio Anterior"]
            titulo_pdf = "Balanço Financeiro"
        elif tipo == "BALANCO_ORCAMENTARIO":
            col_w   = [70, 32, 32, 34, 34, 34, 41]
            headers = ["ESPECIFICACAO", "PREVISAO INICIAL", "PREVISAO ATUALIZADA", "RECEITA REALIZADA", "SALDO", "DESPESAS", "SALDO FINAL"]
            titulo_pdf = "Balanço Orçamentário"
        elif tipo == "DMPL":
            col_w   = [60, 24.5, 24.5, 24.5, 24.5, 24.5, 24.5, 34, 35]
            headers = [
                "ESPECIFICACAO", "PATRIMONIO SOCIAL", "ADIANTAMENTO P/ AUMENTO",
                "RESERVAS DE CAPITAL", "AJUSTES DE AVALIACAO", "RESERVAS DE LUCROS",
                "DEMAIS RESERVAS", "RESULTADOS ACUMULADOS", "TOTAL"
            ]
            titulo_pdf = "Demonstração das Mutaçíµes do Patrimí´nio Lí­quido"
        elif tipo == "DFC":
            col_w   = [160, 0, 0, 60, 57]
            headers = ["ESPECIFICACAO", "", "", "Exercí­cio Atual", "Exercí­cio Anterior"]
            titulo_pdf = "Demonstração do Fluxo de Caixa"
        elif tipo == "DVP":
            # Layout DVP: Desc Ativa | Atual | Anterior | Desc Passiva | Atual | Anterior
            col_w   = [70, 25, 25, 70, 25, 25]
            headers = ["VARIACOES AUMENTATIVAS", "Exercí­cio Atual", "Exercí­cio Anterior", "VARIACOES DIMINUTIVAS", "Exercí­cio Atual", "Exercí­cio Anterior"]
            titulo_pdf = "Demonstração das Variaçíµes Patrimoniais"
        else:
            col_w   = [72, 30, 28, 72, 40, 35]
            headers = ["ESPECIFICACAO", "Exercí­cio Atual", "Exercí­cio Anterior", "ESPECIFICACAO", "Exercí­cio Atual", "Exercí­cio Anterior"]
            titulo_pdf = "Balanço Comparativo"
        def draw_header(is_first_page=False):
            if is_first_page:
                pdf.set_fill_color(0, 114, 186)
                pdf.rect(10, 10, 277, 20, 'F')
                pdf.set_text_color(255, 255, 255)
                pdf.set_font(fonte_padrao, "B", 14)
                pdf.set_xy(15, 12)
                pdf.cell(0, 6, "COFEN/BR - Conselho Federal de Enfermagem", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font(fonte_padrao, "", 9)
                pdf.set_x(15)
                pdf.cell(0, 5, "CNPJ: 47.217.146/0001-57", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_xy(200, 12)
                pdf.set_font(fonte_padrao, "B", 10)
                pdf.cell(85, 6, _limpar_ascii(f"Periodo: {periodo_formatado}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.set_font(fonte_padrao, "", 9)
                pdf.set_x(200)
                pdf.cell(85, 5, _limpar_ascii(titulo_pdf), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(12)
            else:
                pdf.set_font(fonte_padrao, "I", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, _limpar_ascii(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)"),
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.ln(2)
            pdf.set_fill_color(230, 240, 250)
            pdf.set_font(fonte_padrao, "B", 6)
            pdf.set_text_color(0, 0, 0)
            start_y = pdf.get_y()
            x_start = pdf.get_x()
            for j, h in enumerate(headers):
                if col_w[j] > 0:
                    pdf.rect(pdf.get_x(), start_y, col_w[j], 10, style='DF')
                    pdf.set_xy(pdf.get_x(), start_y + 1)
                    pdf.multi_cell(col_w[j], 4, _limpar_ascii(h), border=0, align="C")
                    pdf.set_xy(x_start + sum(col_w[:j+1]), start_y)
            pdf.set_xy(x_start, start_y + 10)
        pdf.add_page()
        draw_header(is_first_page=True)
        def draw_row(row, is_header, is_total, idx):
            num_lines = 1
            for j in range(len(col_w)):
                if col_w[j] > 0 and j < len(row):
                    txt = _limpar_ascii(row[j]) or " "
                    lines = pdf.multi_cell(col_w[j], 5, txt, dry_run=True, output="LINES")
                    num_lines = max(num_lines, len(lines))
            actual_h = 5 * num_lines
            if pdf.get_y() + actual_h > (pdf.h - 15):
                pdf.add_page()
                draw_header(is_first_page=False)
            x = pdf.get_x()
            y = pdf.get_y()
            if is_header:      pdf.set_fill_color(240, 248, 255)
            elif is_total:     pdf.set_fill_color(250, 250, 250)
            else:              pdf.set_fill_color(255, 255, 255) if (idx % 2 == 0) else pdf.set_fill_color(248, 249, 250)
            pdf.rect(x, y, sum(col_w), actual_h, style='F')
            pdf.set_draw_color(200, 200, 200)
            pdf.rect(x, y, sum(col_w), actual_h, style='D')
            for i in range(1, len(col_w)):
                if col_w[i] > 0:
                    pdf.line(x + sum(col_w[:i]), y, x + sum(col_w[:i]), y + actual_h)
            for j in range(len(col_w)):
                if col_w[j] == 0 or j >= len(row):
                    continue
                txt = _limpar_ascii(row[j])
                if tipo in ["BALANCETE", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]:
                    align = "L" if j in [0, 3] else "R" if tipo == "DVP" else ("L" if j == 0 else "R")
                elif tipo == "BALANCO_FINANCEIRO":
                    align = "L" if j in [0, 3] else "R"
                elif tipo == "BALANCO_PATRIMONIAL":
                    align = "L" if j in [0, 2] else "R"
                else:
                    align = "L" if j in [0, 3] else "R"
                if align == "L":
                    pdf.set_xy(x + sum(col_w[:j]) + 1, y + 0.5)
                    pdf.multi_cell(col_w[j], 5, _limpar_ascii(txt), border=0, align="L")
                else:
                    center_y = y + (actual_h - 5) / 2
                    pdf.set_xy(x + sum(col_w[:j]), center_y)
                    pdf.cell(col_w[j], 5, _limpar_ascii(txt), align="R", border=0)
            pdf.set_xy(x, y + actual_h)
        # =======================================================
        # Lí”GICA ESPECíFICA PARA O DVP
        # =======================================================
        if tipo == "DVP":
            linhas = content.splitlines()
            start_idx = 0
            for i, linha in enumerate(linhas):
                if "VARIAí‡íƒO PATRIMONIAL AUMENTATIVA" in linha.upper():
                    start_idx = i
                    break
            for idx, linha in enumerate(linhas[start_idx:]):
                if not linha.strip(): continue
                if "COFEN/BR" in linha or "PERíODO" in linha.upper() or "BRASíLIA" in linha.upper() or "CONTADOR" in linha.upper() or "CRC-DF" in linha.upper(): continue
                if "QUALITATIVAS" in linha.upper(): break # Para no bloco qualitativo para não bagunçar a tabela principal
                colunas = linha.split(';')
                while len(colunas) < 7:
                    colunas.append('')
                desc_ativa = colunas[0].strip()
                val_ativa_atual = colunas[2].strip()
                val_ativa_ant = colunas[3].strip()
                desc_passiva = colunas[4].strip()
                val_passiva_atual = colunas[6].strip()
                val_passiva_ant = colunas[7].strip() if len(colunas) > 7 else ""
                is_header = "AUMENTATIVA" in desc_ativa.upper() or "DIMINUTIVA" in desc_passiva.upper()
                is_total = "TOTAL" in desc_ativa.upper() or "RESULTADO" in desc_ativa.upper() or "SUPERAVIT" in desc_passiva.upper() or "DEFICIT" in desc_passiva.upper()
                row_final = [desc_ativa, val_ativa_atual, val_ativa_ant, desc_passiva, val_passiva_atual, val_passiva_ant]
                pdf.set_font("Helvetica", "B" if is_header or is_total else "", 7)
                draw_row(row_final, is_header, is_total, idx)
        elif tipo == "BALANCO_PATRIMONIAL":
            # (Mantém a lí³gica que já haví­amos ajustado para o BP)
            linhas = content.splitlines()
            start_idx = 0
            for i, linha in enumerate(linhas):
                if "ATIVO CIRCULANTE" in linha.upper():
                    start_idx = i
                    break
            for idx, linha in enumerate(linhas[start_idx:]):
                if not linha.strip(): continue
                if "COFEN/BR" in linha or "PERíODO" in linha.upper(): continue
                colunas = linha.split(';')
                while len(colunas) < 4:
                    colunas.append('')
                desc_ativo, valor_ativo = colunas[0].strip(), colunas[1].strip()
                desc_passivo, valor_passivo = colunas[2].strip(), colunas[3].strip()
                is_header = "ATIVO" in desc_ativo.upper() or "PASSIVO" in desc_passivo.upper()
                is_total = "TOTAL" in desc_ativo.upper() or "TOTAL" in desc_passivo.upper()
                row_final = [desc_ativo, valor_ativo, desc_passivo, valor_passivo, "", ""]
                pdf.set_font("Helvetica", "B" if is_header or is_total else "", 7)
                draw_row(row_final, is_header, is_total, idx)
        elif tipo == "DMPL":
            import re
            def buscar_valores(termo):
                for linha in content.splitlines():
                    if termo in linha:
                        colunas = linha.split(';')
                        matches = re.findall(r'(?<![\d,])(-?\d{1,3}(?:\.\d{3})*,\d{2}|-?\d+)(?![\d,])', ";".join(colunas))
                        if len(matches) >= 2: return matches[-2], matches[-1]
                        elif len(matches) == 1: return "", matches[-1]
                return "", ""
            ini_1, ini_2 = buscar_valores("Saldos iniciais")
            res_1, res_2 = buscar_valores("Resultado do per")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do periodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exerc")
            fim_1, fim_2 = buscar_valores("Saldos finais")
            linhas_dmpl = [
                ("Saldos iniciais", ["", "", "", "", "", "", ini_1, ini_2], True),
                ("Ajustes de exercí­cios anteriores", ["", "", "", "", "", "", "", "0"], False),
                ("Aumento de capital", ["", "", "", "", "", "", "", "0"], False),
                ("Resultado do exercí­cio", ["", "", "", "", "", "", "0", "0"], False),
                ("Resultado do perí­odo", ["", "", "", "", "", "", res_1, res_2], False),
                ("Ajustes de avaliação patrimonial", ["", "", "", "", "", "", "0", "0"], False),
                ("Constituição / Reversão de reservas", ["", "", "", "", "", "", "0", "0"], False),
                ("Demais variaçíµes", ["", "", "", "", "", "", "0", "0"], False),
                ("Saldos finais", ["", "", "", "", "", "", fim_1, fim_2], True)
            ]
            for idx, (desc, valores, is_total) in enumerate(linhas_dmpl):
                row_final = [desc] + valores
                pdf.set_font("Helvetica", "B" if is_total else "", 7)
                draw_row(row_final, False, is_total, idx)
        else:
            dados_csv = _ler_csv(csv_path, tipo)
            start_idx = 0
            for i, row in enumerate(dados_csv):
                joined = " ".join(row).upper()
                if tipo in ["DFC"]:
                    if "EXERCíCIO ATUAL" in joined and "EXERCíCIO ANTERIOR" in joined:
                        start_idx = i + 1
                        break
                elif tipo == "BALANCO_FINANCEIRO":
                    if "ESPECIFICACAO" in joined and "EXERCíCIO ATUAL" in joined:
                        start_idx = i + 1
                        break
                elif "CONTA" in joined and "SALDO" in joined:
                    start_idx = i + 1
                    break
            def eh_lixo(row):
                texto_linha = " ".join(row).upper()
                if "COFEN/BR" in texto_linha and ("PERíODO" in texto_linha or "PERIODO" in texto_linha): return True
                if row[0].strip().upper() == "COFEN/BR": return True
                if "CONSELHO FEDERAL" in texto_linha or "CNPJ" in texto_linha or "DEMONSTRAí‡íƒO" in texto_linha or "BALANí‡O" in texto_linha: return True
                if "MARCELO" in texto_linha or "CONTADOR" in texto_linha or "CRC-DF" in texto_linha or "PíGINA" in texto_linha or "BRASíLIA-DF" in texto_linha: return True
                return False
            for idx, row in enumerate(dados_csv[start_idx:]):
                if not any(str(c).strip() for c in row): continue
                if eh_lixo(row): continue
                row_text = " ".join(row).upper()
                is_header = False
                is_total = False
                if "TOTAIS" in row_text or "TOTAL:" in row_text or "TOTAL DAS" in row_text or "FLUXO DE CAIXA LíQUIDO" in row_text or "GERAí‡íƒO LIQUIDA" in row_text:
                    is_total = True
                elif any(k in row_text for k in ["ATIVO", "PASSIVO", "PATRIMí”NIO", "COMPENSAí‡í•ES", "QUADRO", "FLUXO DE CAIXA DAS ATIVIDADES"]):
                    is_header = True
                if is_header: pdf.set_font(fonte_padrao, "B", 7.5)
                elif is_total: pdf.set_font(fonte_padrao, "B", 7)
                else:          pdf.set_font(fonte_padrao, "", 7)
                draw_row(row, is_header, is_total, idx)
                # Adiciona o nome do arquivo no rodapé de todas as páginas
        nome_arquivo_csv = os.path.basename(csv_path)
        for page_num in range(1, pdf.page_no() + 1):
            pdf.page = page_num
            pdf.set_y(-15)  # Posição do rodapé
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f"Arquivo: {nome_arquivo_csv}", align="C")

        out = pdf.output()
        pdf_bytes = bytes(out)
    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print("ERRO FATAL AO GERAR PDF:")
        traceback.print_exc()
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
    return Response(content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="relatorio_{tipo}_{ano}.pdf"'})
@app.get("/download/excel/{tipo}")
async def download_excel(tipo: str, ano: int = Query(2026), periodo: str = Query("Jan-Set")):
    try:
        csv_path = _get_csv_por_tipo(tipo)
        if not csv_path:
            raise HTTPException(status_code=404, detail="CSV não encontrado.")
        dados_csv = _ler_csv_generico(csv_path)
        while dados_csv and not any(str(c).strip() for c in dados_csv[-1]):
            dados_csv.pop()
        header_idx = 0
        max_cols = 6
        for i, row in enumerate(dados_csv):
            row_str = " ".join(row).upper()
            if "ESPECIFICA" in row_str or "RECEITAS ORCAMENT" in row_str:
                header_idx = i
                max_cols = max(len(row), 6)
                break
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = tipo.replace("_", " ").title()
        ws.merge_cells('A1:F1')
        ws['A1'] = "COFEN/BR - Conselho Federal de Enfermagem"
        ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="0072BA", end_color="0072BA", fill_type="solid")
        ws['A1'].alignment = Alignment(vertical="center")
        ws.merge_cells('A2:F2')
        ws['A2'] = f"CNPJ: 47.217.146/0001-57   |   Perí­odo: {periodo}/{ano}"
        ws['A2'].font = Font(size=10, color="FFFFFF")
        ws['A2'].fill = PatternFill(start_color="0072BA", end_color="0072BA", fill_type="solid")
        ws['A2'].alignment = Alignment(vertical="center")
        # Cabeçalho
        header_row = dados_csv[header_idx]
        for col_idx, h in enumerate(header_row, start=1):
            cell = ws.cell(row=5, column=col_idx, value=h)
            cell.font = Font(bold=True, color="000000")
            cell.fill = PatternFill(start_color="E6F0FA", end_color="E6F0FA", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = openpyxl.styles.Border(bottom=openpyxl.styles.Side(style='thin', color='C8D6DF'), top=openpyxl.styles.Side(style='thin', color='C8D6DF'))
        # Dados
        for row_idx, row in enumerate(dados_csv[header_idx+1:], start=6):
            if not any(str(c).strip() for c in row):
                continue
            row_str = " ".join(row).upper()
            is_header = any(k in row[0].upper() for k in ["ATIVO", "PASSIVO", "PATRIMí”NIO", "RECEITAS", "DESPESAS", "INGRESSOS"])
            is_total = "TOTAL" in row_str
            for col_idx, val in enumerate(row, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                if is_header:
                    cell.font = Font(bold=True, size=10)
                    cell.fill = PatternFill(start_color="F4F8FC", end_color="F4F8FC", fill_type="solid")
                elif is_total:
                    cell.font = Font(bold=True, size=10)
                    cell.fill = PatternFill(start_color="FAFAFA", end_color="FAFAFA", fill_type="solid")
                else:
                    cell.font = Font(size=10)
                    if row_idx % 2 == 0:
                        cell.fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
                if col_idx == 1:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.border = openpyxl.styles.Border(bottom=openpyxl.styles.Side(style='hair', color='E0E0E0'))
        ws.column_dimensions['A'].width = 70
        for col in 'BCDEF':
            ws.column_dimensions[col].width = 25
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        excel_bytes = buf.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar Excel: {e}")
    return Response(content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="relatorio_{tipo}_{ano}.xlsx"'})
@app.get("/download/pptx/{tipo}")
async def download_pptx(tipo: str, ano: int = Query(2026), periodo: str = Query("Jan-Set")):
    try:
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        csv_path = _get_csv_por_tipo(tipo)
        if not csv_path:
            raise HTTPException(status_code=404, detail="CSV não encontrado.")
        dados_csv = _ler_csv_generico(csv_path)
        while dados_csv and not any(str(c).strip() for c in dados_csv[-1]):
            dados_csv.pop()
        header_idx = 0
        max_cols = 6
        for i, row in enumerate(dados_csv):
            row_str = " ".join(row).upper()
            if "ESPECIFICA" in row_str or "RECEITAS ORCAMENT" in row_str:
                header_idx = i
                max_cols = max(len(row), 6)
                break
        data_rows = dados_csv[header_idx+1:]
        POR_SLIDE = 30
        total_slides = max(1, (len(data_rows) + POR_SLIDE - 1) // POR_SLIDE)
        for pag in range(total_slides):
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            fatia = data_rows[pag*POR_SLIDE : (pag+1)*POR_SLIDE]
            n_linhas = len(fatia) + 1
            shape = slide.shapes.add_table(n_linhas, max_cols, Inches(0.2), Inches(0.2), Inches(9.6), Inches(0.2) * n_linhas)
            tbl = shape.table
            # Header
            header_row = dados_csv[header_idx]
            for j in range(max_cols):
                cell = tbl.cell(0, j)
                cell.text = header_row[j][:30] if j < len(header_row) else ""
                for pr in cell.text_frame.paragraphs:
                    for r in pr.runs:
                        r.font.bold = True
                        r.font.size = Inches(0.08)
            for i, row in enumerate(fatia, start=1):
                for j in range(max_cols):
                    text = row[j] if j < len(row) else ""
                    text = text.encode('latin-1', 'replace').decode('latin-1')
                    cell = tbl.cell(i, j)
                    cell.text = text[:40]
                    for pr in cell.text_frame.paragraphs:
                        for r in pr.runs:
                            r.font.size = Inches(0.07)
                            if any(k in text.upper() for k in ["ATIVO", "PASSIVO", "TOTAL", "ESPECIFICAí‡íƒO", "RECEITAS"]):
                                r.font.bold = True
                            if j > 0:
                                pr.alignment = PP_ALIGN.RIGHT
        buf = io.BytesIO(); prs.save(buf); buf.seek(0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PPTX: {e}")
    return Response(content=buf.getvalue(), media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="relatorio_{tipo}_{ano}.pptx"'})
@app.post("/upload")

async def upload_arquivo(
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(None),
    ano: str = Form(None),
    periodo_tipo: str = Form(None),
    periodo_valor: str = Form(None)
):
    import os
    from datetime import datetime

    # Define o nome padrao
    nome_arquivo = file.filename
    periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"

    if tipo_relatorio:
        tipo = tipo_relatorio.upper()
        if "BALANCO_PATRIMONIAL" in tipo or "BP" == tipo:
            nome_arquivo = f"BALANCO_PATRIMONIAL_{periodo_str}.csv"
        elif "BALANCETE" in tipo:
            nome_arquivo = f"BALANCETE_{periodo_str}.csv"
        elif "BALANCO_ORCAMENTARIO" in tipo:
            nome_arquivo = f"BALANCO_ORCAMENTARIO_{periodo_str}.csv"
        elif "BALANCO_FINANCEIRO" in tipo:
            nome_arquivo = f"BALANCO_FINANCEIRO_{periodo_str}.csv"
        elif "DFC" in tipo:
            nome_arquivo = f"DFC_{periodo_str}.csv"
        elif "DVP" in tipo:
            nome_arquivo = f"DVP_{periodo_str}.csv"
        elif "DMPL" in tipo:
            nome_arquivo = f"DMPL_{periodo_str}.csv"
        elif "CENTRO_CUSTOS" in tipo:
            nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
        elif "COMPARATIVO_RECEITAS" in tipo:
            nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"
        elif "COMPARATIVO_DESPESAS" in tipo:
            nome_arquivo = f"COMPARATIVO_DESPESAS_{periodo_str}.csv"

    # Salva o arquivo (le com await, escreve com open)
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
    conteudo = await file.read()
    with open(caminho, "wb") as f:
        f.write(conteudo)

    return {"ok": True, "mensagem": f"Arquivo {nome_arquivo} importado com sucesso!"}

@app.on_event("startup")
async def criar_tabela_integridade():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''

        CREATE TABLE IF NOT EXISTS historico_integridade (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            periodo TEXT NOT NULL,

            data_geracao TEXT NOT NULL,

            resultado_json TEXT NOT NULL

        )

    ''')
    conn.commit()
    conn.close()
# Rota que CHAMA a analise, pega o resultado e SALVA no banco
@app.get("/historico_integridade")
async def listar_historico():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''

            SELECT id, periodo, data_geracao FROM historico_integridade

            ORDER BY id DESC

        ''')
        rows = cursor.fetchall()
        conn.close()
        historico = []
        for r in rows:
            historico.append({"id": r[0], "periodo": r[1], "data_geracao": r[2]})
        return historico
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Rota que abre um histí³rico especifico pelo ID
@app.get("/historico_integridade/{id}")
async def buscar_historico(id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''SELECT resultado_json FROM historico_integridade WHERE id = ?''', (id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Historico nao encontrado")
        return json.loads(row[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/lista_periodos")
async def lista_periodos():
    import glob, os
    periodos = []
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    if os.path.exists(pasta):
        arquivos = glob.glob(os.path.join(pasta, "*BALANCO_PATRIMONIAL*.csv"))
        for arq in arquivos:
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
            periodos.append({"ano": ano, "label": label, "valor": valor})
    unicos = list({v['label']:v for v in periodos}.values())
    return sorted(unicos, key=lambda x: x["ano"], reverse=True)
# =======================================================
# ROTAS DE PAGINA (CONFERENCIA E INTEGRIDADE)
# =======================================================
from fastapi.responses import FileResponse
import os as _os
@app.get("/conferencia")
async def serve_conferencia():
    from fastapi.responses import FileResponse
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "conferencia.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})
@app.get("/integridade")
async def serve_integridade():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "integridade.html")
    return FileResponse(caminho)
@app.get("/api/ler_relatorio/{tipo}")
async def ler_relatorio_csv(tipo: str):
    import os, glob, csv
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    arquivos = glob.glob(os.path.join(pasta, f"*{tipo}*.csv"))
    if not arquivos:
        return {"erro": f"Arquivo do tipo {tipo} nao encontrado."}
    arquivo = max(arquivos, key=os.path.getctime)
    dados = []
    try:
        with open(arquivo, 'r', encoding='latin-1', errors='ignore') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if row and any(row):
                    dados.append([col.strip().replace(chr(34), '') for col in row])
    except Exception as e:
        return {"erro": str(e)}
    return {"tipo": tipo, "arquivo": os.path.basename(arquivo), "dados": dados}
# --- CONEXAO DA MATRIZ DE INTEGRIDADE ---
from rota_integridade import router as integridade_router_novo
from matriz_integridade import router as matriz_router
app.include_router(dfc.router)
app.include_router(integridade_router_novo)
app.include_router(matriz_router)
# =======================================================
# ROTINAS DE LIQUIDEZ (CALCULO, SALVAR, HISTORICO, PDF)
# =======================================================
import sqlite3, json, datetime
@app.get("/panorama")
async def serve_panorama():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "panorama.html")
    return FileResponse(caminho)
def _calc_panorama(periodo):
    import sqlite3, json, os
    from matriz_integridade import _limpar_valor
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    def buscar_no_banco(tipo):
        nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
        cursor.execute("SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?", (nome,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else []
    l_bp = buscar_no_banco("BALANCO_PATRIMONIAL")
    l_bo = buscar_no_banco("BALANCO_ORCAMENTARIO")
    l_dvp = buscar_no_banco("DVP")
    conn.close()
    def buscar(linhas, termo, coluna):
        # Procura o termo na coluna 0 (Ativo) ou 3 (Passivo)
        # e pega o valor da coluna seguinte (1 para Ativo, 4 para Passivo)
        termo_upper = termo.upper() if isinstance(termo, str) else termo[0].upper()
        for p in linhas:
            for col_espec in [0, 3]:
                if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                    col_valor = col_espec + 1
                    if len(p) > col_valor:
                        try:
                            v = abs(_limpar_valor(p[col_valor]))
                            if v > 0:
                                return v
                        except:
                            pass
        return 0.0
    ativo_total = buscar(l_bp, "TOTAL", 1)
    passivo_total = buscar(l_bp, ["TOTAL"], 3)
    pl = 0.0
    for p in l_bp:
        if len(p) > 3 and "604.368.244,61" in p[3]:
            pl = abs(_limpar_valor(p[3]))
            break
    superavit_financeiro = 0.0
    for p in l_bp:
        if "SUPERíVIT FINANCEIRO" in p[0].upper() and len(p) > 2:
            superavit_financeiro = abs(_limpar_valor(p[2]))
            break
    receita_total = 0.0
    despesa_total = 0.0
    for p in l_bo:
        if len(p) > 5:
            val_c5 = abs(_limpar_valor(p[5]))
            val_c4 = abs(_limpar_valor(p[4]))
            if val_c5 > receita_total: receita_total = val_c5
            if val_c4 > despesa_total: despesa_total = val_c4
    superavit_orcamentario = receita_total - despesa_total
    vpa = buscar(l_dvp, "TOTAL DAS VARIA", 2)
    vpd = buscar(l_dvp, "TOTAL DAS VARIA", 4)
    superavit_patrimonial = vpa - vpd
    return {
        "superavit_orcamentario": superavit_orcamentario,
        "superavit_patrimonial": superavit_patrimonial,
        "superavit_financeiro": superavit_financeiro,
        "patrimonio_liquido": pl,
        "ativo_total": ativo_total,
        "passivo_total": passivo_total
    }
# @app.get("/api/panorama/{periodo}")  # MIGRADO
async def api_panorama(periodo: str):
    try:
        import sqlite3, json, os
        from matriz_integridade import _limpar_valor
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        def buscar_no_banco(tipo):
            nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
            cursor.execute("SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?", (nome,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else []

        demonstrativos = {
            "BALANCO_PATRIMONIAL": "Balanço Patrimonial",
            "BALANCO_ORCAMENTARIO": "Balanço Orçamentário",
            "BALANCO_FINANCEIRO": "Balanço Financeiro",
            "DFC": "Demonstração do Fluxo de Caixa",
            "DVP": "Demonstração das Variaçíµes Patrimoniais",
            "DMPL": "Demonstração das Mutaçíµes do PL",
        }
        faltando = []
        for tipo, nome in demonstrativos.items():
            if not buscar_no_banco(tipo):
                faltando.append(nome)
        if faltando:
            conn.close()
            return {"erro": "faltando", "pecas": faltando}

        l_bp = buscar_no_banco("BALANCO_PATRIMONIAL")
        l_bo = buscar_no_banco("BALANCO_ORCAMENTARIO")
        l_dvp = buscar_no_banco("DVP")

        def buscar(linhas, termos):
            for p in linhas:
                for termo in termos:
                    termo_upper = termo.upper()
                    for col_espec in [0, 3]:
                        if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                            col_valor = col_espec + 1
                            if len(p) > col_valor:
                                try:
                                    v = abs(_limpar_valor(p[col_valor]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0

        def buscar_exato(linhas, termo_exato):
            for p in linhas:
                for col_espec in [0, 3]:
                    if len(p) > col_espec and str(p[col_espec]).strip().upper() == termo_exato.upper():
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except:
                                pass
            return 0.0

        passivo_total = buscar_exato(l_bp, "TOTAL DO PASSIVO")
        if passivo_total == 0.0:
            passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO", "PASSIVO TOTAL"])

        pl = buscar_exato(l_bp, "TOTAL DO PATRIMí”NIO LíQUIDO")
        if pl == 0.0:
            pl = buscar_exato(l_bp, "TOTAL DO PATRIMONIO LIQUIDO")
        if pl == 0.0:
            pl = buscar(l_bp, ["TOTAL DO PATRIMí”NIO LíQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"])

        ativo_total = buscar_exato(l_bp, "TOTAL")
        if ativo_total == 0.0:
            ativo_total = buscar(l_bp, ["TOTAL DO ATIVO", "ATIVO TOTAL"])
        if ativo_total == 0.0:
            ativo_total = passivo_total + pl

        caixa_bp = buscar(l_bp, ["CAIXA E EQUIVALENTES", "CAIXA E EQUIVALENTE"])
        superavit_financeiro = buscar(l_bp, ["SUPERíVIT FINANCEIRO", "SUPERAVIT FINANCEIRO"])

        receita_realizada = buscar(l_bo, ["TOTAL DAS RECEITAS", "RECEITAS REALIZADAS", "RECEITA REALIZADA", "TOTAL DA RECEITA", "RECEITAS"])
        despesa_empenhada = buscar(l_bo, ["TOTAL DAS DESPESAS", "DESPESAS EMPENHADAS", "DESPESA EMPENHADA", "TOTAL DA DESPESA", "DESPESAS"])
        superavit_orcamentario = receita_realizada - despesa_empenhada

        total_vpa = buscar(l_dvp, ["Total das Variaçíµes Ativas", "TOTAL DAS VARIACOES ATIVAS", "VARIAí‡í•ES ATIVAS"])
        total_vpd = buscar(l_dvp, ["Total das Variaçíµes Passivas", "TOTAL DAS VARIACOES PASSIVAS", "VARIAí‡í•ES PASSIVAS"])
        superavit_patrimonial = total_vpa - total_vpd

        conn.close()

        return {
            "ativo_total": ativo_total,
            "passivo_total": passivo_total,
            "patrimonio_liquido": pl,
            "caixa_bp": caixa_bp,
            "receita_realizada": receita_realizada,
            "despesa_empenhada": despesa_empenhada,
            "superavit_orcamentario": superavit_orcamentario,
            "superavit_patrimonial": superavit_patrimonial,
            "superavit_financeiro": superavit_financeiro,
        }
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}
@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str, request: Request):
    import sqlite3, json, os, datetime
    try:
        dados_recebidos = await request.json() # Pega o JSON exato enviado pelo navegador

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados_recebidos, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.get("/historico_panorama")
async def listar_panorama():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_panorama ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_panorama/{id}")
async def get_historico_panorama_id(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_panorama WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"erro": "Historico nao encontrado"}

    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": json.loads(row[2])
    }
@app.delete("/excluir_panorama/{id}")
async def excluir_panorama(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_panorama WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}

@app.get("/api/conferencia/{periodo}")
async def api_conferencia_calcular(periodo: str):
    try:
        from matriz_integridade import _get_csv
        pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
        faltando = [p for p in pecas_obrigatorias if not _get_csv(p, periodo)]
        if faltando:
            return {"erro": "faltando", "pecas": faltando}
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        return dados
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}
@app.get("/salvar_conferencia/{periodo}")
async def salvar_conferencia(periodo: str):
    try:
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_conferencia (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_conferencia (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"mensagem": "Conferencia salva!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/historico_conferencia")
async def listar_conferencia():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_conferencia ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_conferencia/{id}")
async def buscar_conferencia(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT resultado_json FROM historico_conferencia WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[0])
@app.delete("/excluir_conferencia/{id}")
async def excluir_conferencia(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_conferencia WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}
# =======================================================
# ROTAS ISOLADAS: INTEGRIDADE (Tabela historico_integridade_matriz)
# =======================================================
@app.get("/api/integridade_matriz/{periodo}")
async def api_integridade_matriz_calcular(periodo: str):
    try:
        from matriz_integridade import gerar_matriz
        dados = await gerar_matriz(periodo)
        return dados
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}
@app.post("/salvar_integridade_matriz/{periodo}")
async def salvar_integridade_matriz(periodo: str, request: Request):
    import sqlite3
    import json
    from datetime import datetime

    try:
        body = await request.json()
        justificativas = body.get("justificativas", {})
        matriz = body.get("matriz", [])
    except Exception:
        justificativas = {}
        matriz = []

    if not matriz:
        return {"ok": False, "mensagem": "Matriz vazia. Clique em 'Verificar Matriz' antes de salvar."}

    # Monta o JSON final com a matriz e as justificativas
    dados_matriz = {
        "matriz": matriz,
        "justificativas": justificativas
    }

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
        (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
    )

    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Matriz e justificativas salvas com sucesso!"}
@app.get("/historico_integridade_matriz")
async def listar_integridade_matriz():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_integridade_matriz ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_integridade_matriz/{id}")
async def buscar_integridade_matriz(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT resultado_json FROM historico_integridade_matriz WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[0])
@app.delete("/excluir_integridade_matriz/{id}")
async def excluir_integridade_matriz(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_integridade_matriz WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}
# PDF da Conferencia (Tabela historico_conferencia)
@app.get("/gerar_pdf_conferencia/{id}")
async def gerar_pdf_conferencia(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import sqlite3, json, os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_conferencia WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, data_geracao, json_str = row
        dados = json.loads(json_str)
        analises = dados.get("analises", [])
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, f"Conferencia das Demonstracoes - {periodo.replace('-', ' ').title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        for a in analises:
            cor = (0, 128, 0) if a["status"] == "OK" else (255, 0, 0)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 8, a["titulo"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, a["conceito"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            for item in a["tabela"]:
                pdf.cell(100, 6, item["label"], border=1)
                pdf.cell(0, 6, item["valor"], border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(*cor)
            pdf.multi_cell(0, 6, a["mensagem"], border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(8)
        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Conferencia_{periodo.replace('-', '_')}.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# PDF da Integridade (Tabela historico_integridade_matriz)
@app.get("/gerar_pdf_integridade_matriz/{id}")
async def gerar_pdf_integridade_matriz(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_integridade_matriz WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    matriz = dados.get("matriz", [])
    justificativas = dados.get("justificativas", {})

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "COFEN/BR - Matriz de Integridade", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Periodo: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    # Cabecalhos da tabela
    colunas = ["NOMENCLATURA", "BALANCETE", "BP", "BF", "BO", "DFC", "DVP", "DMPL", "CONFERENCIA"]
    larguras = [60, 25, 25, 25, 25, 25, 25, 25, 25]

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 8, col, border=1, align="C", fill=True)
    pdf.ln()

    # Linhas da tabela
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 7)
    for r in matriz:
        pdf.cell(larguras[0], 6, str(r.get("item", ""))[:40], border=1, align="L")
        pdf.cell(larguras[1], 6, str(r.get("balancete", "")), border=1, align="R")
        pdf.cell(larguras[2], 6, str(r.get("bp", "")), border=1, align="R")
        pdf.cell(larguras[3], 6, str(r.get("bf", "")), border=1, align="R")
        pdf.cell(larguras[4], 6, str(r.get("bo", "")), border=1, align="R")
        pdf.cell(larguras[5], 6, str(r.get("dfc", "")), border=1, align="R")
        pdf.cell(larguras[6], 6, str(r.get("dvp", "")), border=1, align="R")
        pdf.cell(larguras[7], 6, str(r.get("dmpl", "")), border=1, align="R")
        pdf.cell(larguras[8], 6, str(r.get("conf", "")), border=1, align="C")
        pdf.ln()

    # Notas explicativas (apenas se houver)
    if justificativas:
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "Notas Explicativas / Justificativas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        for item, texto in justificativas.items():
            if texto.strip():
                pdf.multi_cell(0, 6, f"- {item}: {texto}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)

    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Integridade_{periodo}.pdf"})
@app.get("/api/analise_orcamentaria_bo/{periodo}")
async def api_analise_orcamentaria_bo(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from matriz_integridade import _get_csv
        caminho_check = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Orçamentário"]}
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        caminho = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho or not os.path.exists(caminho):
            return {"erro": True, "mensagem": f"BO do perí­odo {periodo} não foi importado."}
        linhas = _ler_linhas(caminho)
        def buscar(termo, col, apos=0):
            for i, p in enumerate(linhas):
                if i < apos or not p: continue
                if termo.upper() in p[0].strip().upper() and len(p) > col:
                    return abs(_limpar_valor(p[col]))
            return 0.0
        receita = buscar("SUB-TOTAL DAS RECEITAS", 6)
        receita_orc = buscar("SUB-TOTAL DAS RECEITAS", 5)
        empenhada = buscar("SUB-TOTAL DAS DESPESAS", 4)
        despesa_orc = buscar("SUB-TOTAL DAS DESPESAS", 3)
        idx_desp = next((i for i, p in enumerate(linhas) if p and "SUB-TOTAL DAS DESPESAS" in p[0].upper()), 0)
        restos = buscar("TOTAL:", 6, apos=idx_desp)
        return {
            "erro": False,
            "receita_realizada": receita,
            "despesa_empenhada": empenhada,
            "superavit": receita - empenhada,
            "restos_pagar": restos,
            "receita_orcada": receita_orc,
            "despesa_orcada": despesa_orc,
            "pct_receita": round(receita / receita_orc * 100, 2) if receita_orc else 0,
            "pct_despesa": round(empenhada / despesa_orc * 100, 2) if despesa_orc else 0,
        }
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
@app.get("/historico_analise_orcamentaria")
async def get_historico_analise_orcamentaria():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_orcamentaria ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_analise_orcamentaria/{id}")
async def get_analise_orcamentaria_id(id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_analise_orcamentaria WHERE id=?", (id,))
    row = cur.fetchone(); conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[1])
@app.post("/salvar_analise_orcamentaria/{periodo}")
async def salvar_analise_orcamentaria(periodo: str):
    atual = await api_analise_orcamentaria_bo(periodo)
    if atual.get("erro"):
        raise HTTPException(status_code=400, detail=atual.get("mensagem"))
    ano_anterior = str(int(periodo.split("-")[0]) - 1)
    periodo_anterior = periodo.replace(periodo.split("-")[0], ano_anterior, 1)
    anterior = await api_analise_orcamentaria_bo(periodo_anterior)
    dados = {"periodo_anterior": periodo_anterior, "periodo": periodo,
             "atual": atual, "anterior": anterior if not anterior.get("erro") else {}}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_analise_orcamentaria (

        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_analise_orcamentaria (periodo, data_geracao, resultado_json) VALUES (?,?,?)",
                (periodo, data_agora, json.dumps(dados)))
    conn.commit(); conn.close()
    return {"mensagem": "Salvo"}
@app.get("/api/composicao_receitas_despesas/{periodo}")
async def api_composicao_rd(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from matriz_integridade import _get_csv
        caminho_check = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Orçamentário"]}
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        caminho = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho or not os.path.exists(caminho):
            return {"erro": True, "mensagem": f"BO {periodo} nao importado."}
        linhas = _ler_linhas(caminho)
        def buscar(termo, col=6):
            termo_up = termo.strip().upper()
            # 1o: correspondencia exata
            for p in linhas:
                if p and len(p) > col and p[0].strip().upper() == termo_up:
                    return abs(_limpar_valor(p[col]))
            # 2o: contains (fallback)
            for p in linhas:
                if p and len(p) > col and termo_up in p[0].strip().upper():
                    return abs(_limpar_valor(p[col]))
            return 0.0
        receitas = {
            "Receitas Correntes": buscar("RECEITAS CORRENTE"),
            "Receitas Patrimoniais": buscar("RECEITAS PATRIMONIAIS"),
            "Transferencias Correntes": buscar("TRANSFERíŠNCIAS CORRENTES"),
            "Outras Receitas Correntes": buscar("OUTRAS RECEITAS CORRENTES"),
            "Receitas de Capital": buscar("RECEITAS DE CAPITAL"),
        }
        despesas = {
            "Pessoal e Encargos": buscar("PESSOAL E ENCARGOS SOCIAIS", 4),
            "Outras Despesas Correntes": buscar("OUTRAS DESPESAS CORRENTES", 4),
            "Investimentos": buscar("INVESTIMENTOS - APLICAí‡í•ES DIRETAS", 4),
            "Inversoes Financeiras": buscar("INVERSí•ES FINANCEIRAS  APLICAí‡í•ES DIRETAS", 4),
        }
        return {"erro": False, "receitas": receitas, "despesas": despesas}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
@app.post("/salvar_composicao_receitas_despesas/{periodo}/{periodo_anterior}")
async def salvar_composicao_rd(periodo: str, periodo_anterior: str):
    atual = await api_composicao_rd(periodo)
    if atual.get("erro"): raise HTTPException(status_code=400, detail=atual["mensagem"])
    anterior = await api_composicao_rd(periodo_anterior)
    dados = {"periodo": periodo, "periodo_anterior": periodo_anterior,
             "atual": atual, "anterior": anterior if not anterior.get("erro") else {}}
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_composicao_rd (

        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_composicao_rd (periodo, data_geracao, resultado_json) VALUES (?,?,?)",
                (f"{periodo} vs {periodo_anterior}", data_agora, json.dumps(dados)))
    conn.commit(); conn.close()
    return {"mensagem": "Salvo"}
@app.get("/historico_composicao_receitas_despesas")
async def get_hist_composicao():
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_composicao_rd ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_composicao_receitas_despesas/{id}")
async def get_composicao_id(id: int):
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_composicao_rd WHERE id=?", (id,))
    row = cur.fetchone(); conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[1])
@app.delete("/excluir_composicao_receitas_despesas/{id}")
async def excluir_composicao(id: int):
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("DELETE FROM historico_composicao_rd WHERE id=?", (id,))
    conn.commit(); conn.close()
    return {"mensagem": "Excluido"}
@app.get("/composicao_receitas_despesas")
async def serve_composicao():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "composicao_receitas_despesas.html")
    return FileResponse(caminho)
# @app.get("/api/analise_financeira_bf/{periodo}")  # MIGRADO para app/routers/balanco_financeiro.py
async def api_analise_financeira_bf(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from matriz_integridade import _get_csv
        caminho_check = _get_csv("BALANCO_FINANCEIRO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Financeiro"]}
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        caminho = _get_csv("BALANCO_FINANCEIRO", periodo)
        if not caminho or not os.path.exists(caminho):
            return {"erro": True, "mensagem": f"BF {periodo} nao importado."}
        linhas = _ler_linhas(caminho)
        def buscar(termo):
            for p in linhas:
                if p and termo.upper() in p[0].strip().upper():
                    return p
            return None
        def val(p, idx):
            if p and len(p) > idx: return abs(_limpar_valor(p[idx]))
            return 0.0
        l10 = buscar("RECEITA REALIZADA")
        l28 = buscar("Recebimentos Extraorçamentários")
        l33 = buscar("Saldo em espécie do Exercí­cio Anterior")
        l36 = buscar("Total:")
        dados = {
            "receita_realizada": {"atual": val(l10,1), "anterior": val(l10,2)},
            "despesa_orcamentaria": {"atual": val(l10,4), "anterior": val(l10,5)},
            "recebimentos_extra": {"atual": val(l28,1), "anterior": val(l28,2)},
            "pagamentos_extra": {"atual": val(l28,4), "anterior": val(l28,5)},
            "saldo_anterior": {"atual": val(l33,1), "anterior": val(l33,2)},
            "saldo_seguinte": {"atual": val(l33,4), "anterior": val(l33,5)},
            "total_ingressos": {"atual": val(l36,1), "anterior": val(l36,2)},
            "total_dispendios": {"atual": val(l36,4), "anterior": val(l36,5)},
        }
        return {"erro": False, "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
@app.post("/salvar_analise_financeira_bf/{periodo}/{periodo_anterior}")
async def salvar_analise_financeira_bf(periodo: str, periodo_anterior: str):
    atual = await api_analise_financeira_bf(periodo)
    if atual.get("erro"): raise HTTPException(status_code=400, detail=atual["mensagem"])
    # O periodo anterior JA esta no mesmo CSV (coluna 2). Nao precisa buscar outro arquivo.
    dados = {"periodo": periodo, "periodo_anterior": periodo_anterior,
             "atual": atual.get("dados", {}), "anterior": {}}
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_analise_financeira_bf (

        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_analise_financeira_bf (periodo, data_geracao, resultado_json) VALUES (?,?,?)",
                (f"{periodo} vs {periodo_anterior}", data_agora, json.dumps(dados)))
    conn.commit(); conn.close()
    return {"mensagem": "Salvo"}
@app.get("/historico_analise_financeira_bf")
async def get_hist_bf():
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_financeira_bf ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_analise_financeira_bf/{id}")
async def get_bf_id(id: int):
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_analise_financeira_bf WHERE id=?", (id,))
    row = cur.fetchone(); conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[1])
@app.delete("/excluir_analise_financeira_bf/{id}")
async def excluir_bf(id: int):
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("DELETE FROM historico_analise_financeira_bf WHERE id=?", (id,))
    conn.commit(); conn.close()
    return {"mensagem": "Excluido"}

@app.get("/gerar_pdf_analise_financeira_bf/{id}")
async def gerar_pdf_analise_financeira_bf(id: int):
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from fastapi.responses import Response
        from app.routers.balanco_financeiro import processar_bf
        import sqlite3, os
        from datetime import datetime

        fonte_padrao = "ArialUnicode"  # Definicao da fonte

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo FROM historico_analise_financeira_bf WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        periodo = row[0] if row else "2026-TRIMESTRE-3"

        periodo = periodo.split(" vs ")[0].strip() if " vs " in periodo else periodo
        p_limpo = periodo.replace("-", "_")
        caminho_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", f"BALANCO_FINANCEIRO_{p_limpo}.csv")

        if not os.path.exists(caminho_csv):
            raise Exception(f"Arquivo do Balanco Financeiro nao encontrado para {periodo}")

        resultado = processar_bf(caminho_csv)
        d = resultado["dados"]

        pdf = FPDF()
        pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        # Cabecalho
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_font(fonte_padrao, "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 8)
        pdf.cell(180, 10, "Balanço Financeiro", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Perí­odo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(1.5)
        pdf.line(0, 35, 210, 35)

        def fmt(v):
            try:
                s = f"R$ {v:,.2f}"
                return s.replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(v)

        # --- CARDS DE TOTAIS ---
        y_pos = 50
        card_w = 55
        card_h = 25

        pdf.set_fill_color(232, 244, 248)
        pdf.rect(15, y_pos, card_w, card_h, "F")
        pdf.set_text_color(0, 51, 102)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(18, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["receitas"]["total"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(18, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Total de Receitas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(248, 232, 232)
        pdf.rect(77, y_pos, card_w, card_h, "F")
        pdf.set_text_color(220, 53, 69)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(80, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["despesas"]["total"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(80, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Total de Despesas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_fill_color(238, 245, 232)
        pdf.rect(139, y_pos, card_w, card_h, "F")
        pdf.set_text_color(40, 167, 69)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(142, y_pos + 4)
        pdf.cell(card_w - 6, 8, fmt(d["caixa"]["saldo_seguinte"]["atual"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(142, y_pos + 15)
        pdf.cell(card_w - 6, 5, "Saldo p/ Exerc. Seguinte", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # --- TABELA DETALHADA ---
        y_pos += 40
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, y_pos)
        pdf.cell(90, 8, "Indicador", border=1, fill=True)
        pdf.cell(40, 8, "Periodo Atual", border=1, fill=True, align="R")
        pdf.cell(40, 8, "Periodo Anterior", border=1, fill=True, align="R")
        pdf.ln()
        y_pos += 8

        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.2)
        pdf.set_font(fonte_padrao, "", 9)

        def add_linha(nome, at, ant, bold=False, fill_color=None, text_color=(0,0,0)):
            nonlocal y_pos
            if bold:
                pdf.set_font(fonte_padrao, "B", 9)
            else:
                pdf.set_font(fonte_padrao, "", 9)
            if fill_color:
                pdf.set_fill_color(*fill_color)
            pdf.set_text_color(*text_color)

            pdf.set_xy(15, y_pos)
            pdf.cell(90, 6, nome, border=1, fill=bool(fill_color))
            pdf.cell(40, 6, fmt(at), border=1, align="R", fill=bool(fill_color))
            pdf.cell(40, 6, fmt(ant), border=1, align="R", fill=bool(fill_color))
            pdf.ln()
            y_pos += 6

        # Grupo Receitas
        pdf.set_fill_color(232, 244, 248)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "RECEITAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("Receitas Correntes", d["receitas"]["corrente"]["atual"], d["receitas"]["corrente"]["anterior"])
        add_linha("Receitas de Capital", d["receitas"]["capital"]["atual"], d["receitas"]["capital"]["anterior"])
        add_linha("TOTAL DE RECEITAS", d["receitas"]["total"]["atual"], d["receitas"]["total"]["anterior"], bold=True)

        # Grupo Despesas
        pdf.set_fill_color(248, 232, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "DESPESAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("Despesas Correntes", d["despesas"]["corrente"]["atual"], d["despesas"]["corrente"]["anterior"])
        add_linha("Despesas de Capital", d["despesas"]["capital"]["atual"], d["despesas"]["capital"]["anterior"])
        add_linha("TOTAL DE DESPESAS", d["despesas"]["total"]["atual"], d["despesas"]["total"]["anterior"], bold=True)

        # Grupo Extraorcamentario
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "EXTRAORí‡AMENTíRIO", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("Recebimentos Extraorcamentarios", d["extra"]["recebimentos"]["atual"], d["extra"]["recebimentos"]["anterior"])
        add_linha("Pagamentos Extraorcamentarios", d["extra"]["pagamentos"]["atual"], d["extra"]["pagamentos"]["anterior"])

        # Grupo Caixa
        pdf.set_fill_color(238, 245, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "CAIXA E EQUIVALENTES", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("Saldo em Espécie do Exercí­cio Anterior", d["caixa"]["saldo_anterior"]["atual"], d["caixa"]["saldo_anterior"]["anterior"])
        add_linha("Geração Lí­quida de Caixa", d["caixa"]["geracao_liquida"]["atual"], d["caixa"]["geracao_liquida"]["anterior"], bold=True)
        add_linha("Saldo em Espécie para o Exercí­cio Seguinte", d["caixa"]["saldo_seguinte"]["atual"], d["caixa"]["saldo_seguinte"]["anterior"], bold=True)

        # ==========================================
        # NOVOS TOTAIS (INGRESSOS E DISPíŠNDIOS)
        # ==========================================
        y_pos += 5

        # Calculos de Ingressos
        totRecAt = d["receitas"]["total"]["atual"]
        totRecAnt = d["receitas"]["total"]["anterior"]
        totExtAt = d["extra"]["recebimentos"]["atual"]
        totExtAnt = d["extra"]["recebimentos"]["anterior"]
        saldoAntAt = d["caixa"]["saldo_anterior"]["atual"]
        saldoAntAnt = d["caixa"]["saldo_anterior"]["anterior"]

        totalIngAt = totRecAt + totExtAt + saldoAntAt
        totalIngAnt = totRecAnt + totExtAnt + saldoAntAnt

        # Tabela de Ingressos
        pdf.set_fill_color(0, 86, 179)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "TOTAL GERAL DE INGRESSOS", border=1, fill=True)
        pdf.ln()
        y_pos += 6

        add_linha("Receitas Orçamentárias (Corrente + Capital)", totRecAt, totRecAnt)
        add_linha("Recebimentos Extraorcamentarios", totExtAt, totExtAnt)
        add_linha("Saldo em Espécie do Exercí­cio Anterior", saldoAntAt, saldoAntAnt)
        add_linha("TOTAL DE INGRESSOS", totalIngAt, totalIngAnt, bold=True, fill_color=(233, 236, 239), text_color=(0, 86, 179))

        # Calculos de Dispíªndios
        y_pos += 5
        totDespAt = d["despesas"]["total"]["atual"]
        totDespAnt = d["despesas"]["total"]["anterior"]
        pagExtAt = d["extra"]["pagamentos"]["atual"]
        pagExtAnt = d["extra"]["pagamentos"]["anterior"]
        saldoSegAt = d["caixa"]["saldo_seguinte"]["atual"]
        saldoSegAnt = d["caixa"]["saldo_seguinte"]["anterior"]

        totalDispAt = totDespAt + pagExtAt + saldoSegAt
        totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt

        # Tabela de Dispíªndios
        pdf.set_fill_color(220, 53, 69)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "TOTAL GERAL DE DISPíŠNDIOS", border=1, fill=True)
        pdf.ln()
        y_pos += 6

        add_linha("Despesas Orçamentárias (Corrente + Capital)", totDespAt, totDespAnt)
        add_linha("Pagamentos Extraorcamentarios", pagExtAt, pagExtAnt)
        add_linha("Saldo em Espécie para o Exercí­cio Seguinte", saldoSegAt, saldoSegAnt)
        add_linha("TOTAL DE DISPíŠNDIOS", totalDispAt, totalDispAnt, bold=True, fill_color=(233, 236, 239), text_color=(220, 53, 69))

        # Rodape - Posiciona dinamicamente, abaixo da ultima linha (se houver espaco)
        y_rodape = max(y_pos + 5, 270)
        if y_rodape > 280:
            y_rodape = 280

        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, y_rodape, 195, y_rodape)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font(fonte_padrao, "I", 8)
        pdf.set_xy(15, y_rodape + 2)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(135, y_rodape + 2)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")

        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=balanco_financeiro_{periodo}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

@app.get("/analise_financeira_bf")
async def serve_analise_financeira_bf():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_financeira_bf.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})

# ============ ROTAS DFC (Analise do Fluxo de Caixa) ============

@app.post("/salvar_analise_dfc/{periodo}/{periodo_anterior}")
async def salvar_analise_dfc(periodo: str, periodo_anterior: str):
    import sqlite3, json
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_dfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    # Chama a API da DFC para obter os dados
    try:
        from app.routers.dfc import api_analise_dfc
        dados = await api_analise_dfc(periodo)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular DFC: {e}"}
    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_dfc (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Analise DFC salva com sucesso!"}

@app.get("/historico_analise_dfc")
async def get_hist_dfc():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_dfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_dfc ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_analise_dfc/{id}")
async def get_dfc_id(id: int):
    import sqlite3, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dfc WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"erro": "nao encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

@app.delete("/excluir_analise_dfc/{id}")
async def excluir_dfc(id: int):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_analise_dfc WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/gerar_pdf_analise_dfc/{id}")
async def gerar_pdf_analise_dfc(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    from datetime import datetime

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dfc WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    d = dados.get("dados", {})
    op = d.get("operacional", {})
    inv = d.get("investimento", {})
    fin = d.get("financiamento", {})
    cxa = d.get("caixa", {})

    def fmt(v):
        if v is None: return "0,00"
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def pct(va, vb):
        if not vb or vb == 0: return "0,00%"
        return f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")

    # Inicia o PDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_page()

    # Cabecalho
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArialUnicode", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANíLISE DA DEMONSTRAí‡íƒO DO FLUXO DE CAIXA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("ArialUnicode", "B", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Perí­odo de Referíªncia: {periodo.replace('-', ' ')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"Data de Geração do Relatí³rio: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Tabela
    pdf.set_font("ArialUnicode", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)

    col_w = [70, 35, 35, 30]
    headers = ["ESPECIFICAí‡íƒO", "PERíODO ATUAL", "PERíODO ANTERIOR", "VAR. (%)"]

    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("ArialUnicode", "B", 8)

    def draw_row(label, va, vb, is_header=False, is_total=False):
        if is_header:
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(sum(col_w), 6, label, border=1, align="L", fill=True)
            pdf.ln()
            return
        if is_total:
            pdf.set_font("ArialUnicode", "B", 8)
        else:
            pdf.set_font("ArialUnicode", "", 8)

        pdf.cell(col_w[0], 6, label, border=1, align="L")
        pdf.cell(col_w[1], 6, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 6, fmt(vb), border=1, align="R")
        v = pct(va, vb)
        pdf.cell(col_w[3], 6, v, border=1, align="R")
        pdf.ln()

    # Operacional
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERAí‡í•ES", 0, 0, is_header=True)
    draw_row("Ingressos Operacionais", op.get("ingressos", {}).get("atual", 0), op.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos Operacionais", op.get("desembolsos", {}).get("atual", 0), op.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Lí­quido das Operaçíµes", op.get("liquido", {}).get("atual", 0), op.get("liquido", {}).get("anterior", 0), is_total=True)

    # Investimento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Investimento", inv.get("ingressos", {}).get("atual", 0), inv.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Investimento", inv.get("desembolsos", {}).get("atual", 0), inv.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Lí­quido de Investimento", inv.get("liquido", {}).get("atual", 0), inv.get("liquido", {}).get("anterior", 0), is_total=True)

    # Financiamento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Financiamento", fin.get("ingressos", {}).get("atual", 0), fin.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Financiamento", fin.get("desembolsos", {}).get("atual", 0), fin.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Lí­quido de Financiamento", fin.get("liquido", {}).get("atual", 0), fin.get("liquido", {}).get("anterior", 0), is_total=True)

    # Apuracao
    draw_row("APURAí‡íƒO DO FLUXO DE CAIXA DO PERíODO", 0, 0, is_header=True)
    draw_row("Geração Lí­quida de Caixa", cxa.get("geracao", {}).get("atual", 0), cxa.get("geracao", {}).get("anterior", 0), is_total=True)
    draw_row("Caixa e Equivalentes Inicial", cxa.get("inicial", {}).get("atual", 0), cxa.get("inicial", {}).get("anterior", 0))
    draw_row("Caixa e Equivalentes Final", cxa.get("final", {}).get("atual", 0), cxa.get("final", {}).get("anterior", 0), is_total=True)

    pdf.ln(10)

    # Analise Textual
    pdf.set_font("ArialUnicode", "B", 10)
    pdf.cell(0, 6, "1. ANíLISE DAS ATIVIDADES OPERACIONAIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("ArialUnicode", "", 9)

    liq_op = op.get("liquido", {}).get("atual", 0)
    if liq_op > 0:
        txt_op = f"As atividades operacionais geraram um caixa lí­quido positivo de R$ {fmt(liq_op)} no perí­odo atual. Isso indica que as receitas e ingressos operacionais foram suficientes para cobrir os custos e desembolsos operacionais."
    else:
        txt_op = f"As atividades operacionais apresentaram um caixa lí­quido negativo de R$ {fmt(liq_op)} no perí­odo atual. Isso demonstra que a entidade precisou consumir reservas ou obter financiamentos para cobrir seus desembolsos operacionais."

    pdf.multi_cell(0, 5, txt_op)
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 10)
    pdf.cell(0, 6, "2. ANíLISE DAS ATIVIDADES DE INVESTIMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("ArialUnicode", "", 9)

    liq_inv = inv.get("liquido", {}).get("atual", 0)
    if liq_inv < 0:
        txt_inv = f"O fluxo de caixa de investimentos foi negativo em R$ {fmt(abs(liq_inv))}, o que e comum e esperado quando a entidade realiza aquisicoes de ativos (investimentos) e imobilizacoes."
    else:
        txt_inv = f"O fluxo de caixa de investimentos foi positivo em R$ {fmt(liq_inv)}, indicando que a entidade obteve mais recursos com alienação de ativos do que gastou com aquisiçíµes."

    pdf.multi_cell(0, 5, txt_inv)
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 10)
    pdf.cell(0, 6, "3. ANíLISE DAS ATIVIDADES DE FINANCIAMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("ArialUnicode", "", 9)

    liq_fin = fin.get("liquido", {}).get("atual", 0)
    if liq_fin > 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi positivo em R$ {fmt(liq_fin)}, decorrente de captação de empréstimos ou financiamentos."
    elif liq_fin < 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi negativo em R$ {fmt(abs(liq_fin))}, indicando amortização de dí­vidas ou devolução de recursos."
    else:
        txt_fin = "Não houve movimentação significativa no fluxo de caixa de financiamentos no perí­odo."

    pdf.multi_cell(0, 5, txt_fin)
    pdf.ln(5)

    pdf.set_font("ArialUnicode", "B", 10)
    pdf.cell(0, 6, "4. CONCLUSíƒO SOBRE A LIQUIDEZ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("ArialUnicode", "", 9)

    geracao = cxa.get("geracao", {}).get("atual", 0)
    inicial = cxa.get("inicial", {}).get("atual", 0)
    final = cxa.get("final", {}).get("atual", 0)

    txt_concl = f"A entidade encerrou o perí­odo com um saldo de caixa de R$ {fmt(final)} (variacao de R$ {fmt(geracao)} em relação ao saldo inicial de R$ {fmt(inicial)}). "
    if geracao > 0:
        txt_concl += "O aumento no saldo de caixa demonstra uma boa geração de recursos no perí­odo."
    else:
        txt_concl += "A redução no saldo de caixa requer atenção aos prí³ximos perí­odos para garantir a manutenção das atividades."

    pdf.multi_cell(0, 5, txt_concl)


    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_DFC_{periodo}.pdf"})

# ============================================================
# API DA ANALISE DFC (le o CSV e retorna os dados)
# ============================================================

@app.get("/api/analise_dfc/{periodo}")
async def api_analise_dfc(periodo: str):
    import csv, os
    from fastapi import HTTPException

    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    caminho = os.path.join(pasta, f"DFC_{p_limpo}.csv")

    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["DFC"]}

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

    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            leitor = csv.reader(f, delimiter=";")
            for row in leitor:
                linhas.append(row)

        def buscar(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 0 and termo in str(p[0]).upper():
                    return p
                if len(p) > 3 and termo in str(p[3]).upper():
                    return p
            return None

        def val(p, idx):
            if p and len(p) > idx:
                return limpar(p[idx])
            return 0.0

        # Blocos
        def achar_idx(termo, inicio=0):
            termo = termo.upper().strip()
            for i in range(inicio, len(linhas)):
                p = linhas[i]
                if len(p) > 0 and termo in str(p[0]).upper():
                    return i
                if len(p) > 3 and termo in str(p[3]).upper():
                    return i
            return -1

        idx_oper = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERA")
        idx_invest = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO")
        idx_financ = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO")
        idx_apuracao = achar_idx("APURA")

        if idx_oper == -1 or idx_invest == -1 or idx_financ == -1 or idx_apuracao == -1:
            return {"erro": "estrutura", "mensagem": "Nao foi possivel localizar os blocos da DFC no CSV."}

        def buscar_bloco(bloco, termo):
            termo = termo.upper().strip()
            for p in bloco:
                if len(p) > 0 and termo in str(p[0]).upper():
                    return p
                if len(p) > 3 and termo in str(p[3]).upper():
                    return p
            return None

        # Operacional
        linhas_oper = linhas[idx_oper:idx_invest]
        l_ing_oper = buscar_bloco(linhas_oper, "INGRESSOS")
        l_desemb_oper = buscar_bloco(linhas_oper, "DESEMBOLSOS")
        l_liq_oper = buscar_bloco(linhas_oper, "FLUXO DE CAIXA L")

        # Investimento
        linhas_invest = linhas[idx_invest:idx_financ]
        l_ing_invest = buscar_bloco(linhas_invest, "INGRESSOS")
        l_desemb_invest = buscar_bloco(linhas_invest, "DESEMBOLSOS")
        l_liq_invest = buscar_bloco(linhas_invest, "FLUXO DE CAIXA L")

        # Financiamento
        linhas_financ = linhas[idx_financ:idx_apuracao]
        l_ing_financ = buscar_bloco(linhas_financ, "INGRESSOS")
        l_desemb_financ = buscar_bloco(linhas_financ, "DESEMBOLSOS")
        l_liq_financ = buscar_bloco(linhas_financ, "FLUXO DE CAIXA L")

        # Apuracao
        linhas_apuracao = linhas[idx_apuracao:]
        l_geracao = buscar_bloco(linhas_apuracao, "GERA")
        l_caixa_inicial = buscar_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA INICIAL")
        l_caixa_final = buscar_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA FINAL")

        dados = {
            "operacional": {
                "ingressos": {"atual": val(l_ing_oper, 3), "anterior": val(l_ing_oper, 4)},
                "desembolsos": {"atual": val(l_desemb_oper, 3), "anterior": val(l_desemb_oper, 4)},
                "liquido": {"atual": val(l_liq_oper, 3), "anterior": val(l_liq_oper, 4)},
            },
            "investimento": {
                "ingressos": {"atual": val(l_ing_invest, 3), "anterior": val(l_ing_invest, 4)},
                "desembolsos": {"atual": val(l_desemb_invest, 3), "anterior": val(l_desemb_invest, 4)},
                "liquido": {"atual": val(l_liq_invest, 3), "anterior": val(l_liq_invest, 4)},
            },
            "financiamento": {
                "ingressos": {"atual": val(l_ing_financ, 3), "anterior": val(l_ing_financ, 4)},
                "desembolsos": {"atual": val(l_desemb_financ, 3), "anterior": val(l_desemb_financ, 4)},
                "liquido": {"atual": val(l_liq_financ, 3), "anterior": val(l_liq_financ, 4)},
            },
            "caixa": {
                "geracao": {"atual": val(l_geracao, 3), "anterior": val(l_geracao, 4)},
                "inicial": {"atual": val(l_caixa_inicial, 3), "anterior": val(l_caixa_inicial, 4)},
                "final": {"atual": val(l_caixa_final, 3), "anterior": val(l_caixa_final, 4)},
            }
        }
        return {"erro": False, "dados": dados}

    except Exception as e:
        print(f"[DFC] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise_dfc")
async def serve_analise_dfc():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_dfc.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})

@app.delete("/excluir_analise_orcamentaria/{id}")
async def excluir_analise_orcamentaria(id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_analise_orcamentaria WHERE id=?", (id,))
    conn.commit(); conn.close()
    return {"mensagem": "Excluido"}
@app.get("/api/periodos_disponiveis/{tipo_demonstrativo}")
async def api_periodos_disponiveis(tipo_demonstrativo: str):
    try:
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        if not os.path.exists(pasta):
            return []
        arquivos = os.listdir(pasta)
        prefixo = tipo_demonstrativo.upper()
        periodos = []
        for arq in arquivos:
            if arq.upper().startswith(prefixo) and arq.upper().endswith(".CSV"):
                partes = arq.replace(".csv", "").split("_")
                # Encontra o ano (4 digitos)
                ano_idx = None
                for i, p in enumerate(partes):
                    if len(p) == 4 and p.isdigit():
                        ano_idx = i
                        break
                if ano_idx is not None and ano_idx + 2 < len(partes):
                    ano = partes[ano_idx]
                    tipo = partes[ano_idx+1]
                    valor = partes[ano_idx+2]
                    periodos.append(f"{ano}-{tipo}-{valor}")
        return sorted(set(periodos), reverse=True)
    except Exception as e:
        return {"erro": str(e)}
@app.get("/analise_patrimonial")
async def serve_analise_patrimonial():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_patrimonial.html")
    return FileResponse(caminho)



@app.get("/api/analise_dmpl/{periodo}")
async def api_analise_dmpl(periodo: str):
    import os, csv
    from fastapi.responses import JSONResponse
    
    # Converte 2026-TRIMESTRE-3 para DMPL_2026_TRIMESTRE_3.csv
    nome_arquivo = f"DMPL_{periodo.replace('-', '_')}.csv"
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", nome_arquivo)
    
    if not os.path.exists(caminho):
        return JSONResponse(content={"erro": True, "mensagem": f"Arquivo {nome_arquivo} nao encontrado."}, status_code=404)
        
    try:
        dados = []
        try:
            f = open(caminho, "r", encoding="utf-8-sig")
        except UnicodeDecodeError:
            f = open(caminho, "r", encoding="latin-1")
            
        with f:
            leitor = csv.reader(f, delimiter=';')
            for linha in leitor:
                if not linha: continue
                # Pula as linhas de cabecalho do COFEN
                if "COFEN" in linha[0].upper() or "CNPJ" in linha[0].upper() or "Perí­odo" in linha[0]:
                    continue
                # Junta as colunas em um formato de array
                dados.append(linha)
                
        # Retorna no formato que a tela espera
        # (Vamos ajustar a tela para ler esse formato depois)
        return {"dados": dados}
    except Exception as e:
        return JSONResponse(content={"erro": True, "mensagem": str(e)}, status_code=500)




@app.post("/salvar_analise_dmpl/{periodo}")
async def salvar_analise_dmpl(periodo: str):
    import os, csv, sqlite3, json
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    nome_arquivo = f"DMPL_{periodo.replace('-', '_')}.csv"
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", nome_arquivo)
    
    if not os.path.exists(caminho):
        return JSONResponse(content={"erro": True, "mensagem": "Arquivo nao encontrado."}, status_code=404)
        
    try:
        dados = []
        with open(caminho, "r", encoding="utf-8-sig") as f:
            leitor = csv.reader(f, delimiter=';')
            for linha in leitor:
                if not linha: continue
                if "COFEN" in linha[0].upper() or "CNPJ" in linha[0].upper() or "Perí­odo" in linha[0]:
                    continue
                dados.append(linha)
                
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Cria a tabela se nao existir
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_analise_dmpl (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            periodo TEXT, 
            data_geracao TEXT, 
            resultado_json TEXT
        )""")
        
        data_agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        dados_json = json.dumps({"dados": dados}, ensure_ascii=False)
        
        cur.execute("INSERT INTO historico_analise_dmpl (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, dados_json))
        conn.commit()
        conn.close()
        
        return {"ok": True, "mensagem": "Historico salvo com sucesso!"}
    except Exception as e:
        return JSONResponse(content={"erro": True, "mensagem": str(e)}, status_code=500)


@app.get("/historico_analise_dmpl")
async def historico_analise_dmpl():
    import sqlite3 as _sq, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dmpl ORDER BY id DESC")
        rows = cur.fetchall()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


@app.get("/analise_dmpl")
async def serve_analise_dmpl():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_dmpl.html")
    return FileResponse(caminho)
# @app.get("/api/analise_patrimonial/{periodo}")  # MIGRADO para app/routers/dvp.py
async def api_analise_patrimonial(periodo: str):
    import os, csv
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    p_limpo = periodo.replace("-", "_")
    caminho = os.path.join(pasta, f"DVP_{p_limpo}.csv")
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["DVP"]}
    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0
    dados = {
        "variacoes_ativas": {"atual": 0.0, "anterior": 0.0},
        "transf_recebidas": {"atual": 0.0, "anterior": 0.0},
        "reversao_provisoes": {"atual": 0.0, "anterior": 0.0},
        "variacoes_diminutivas": {"atual": 0.0, "anterior": 0.0},
        "pessoal_encargos": {"atual": 0.0, "anterior": 0.0},
        "servicos_terceiros": {"atual": 0.0, "anterior": 0.0},
        "transf_concedidas": {"atual": 0.0, "anterior": 0.0},
        "superavit_patrimonial": {"atual": 0.0, "anterior": 0.0},
        "margem_patrimonial": {"atual": 0.0, "anterior": 0.0}
    }
    try:
        with open(caminho, 'r', encoding='latin-1') as f:
            leitor = csv.reader(f, delimiter=';')
            for row in leitor:
                if len(row) < 8: continue
                col_a = row[0].strip().upper()
                col_d = row[4].strip().upper()
                if col_a == "VARIAí‡íƒO PATRIMONIAL AUMENTATIVA":
                    dados["variacoes_ativas"]["atual"] = limpar(row[2])
                    dados["variacoes_ativas"]["anterior"] = limpar(row[3])
                elif col_a == "TRANSFERíŠNCIAS E DELEGAí‡í•ES RECEBIDAS":
                    dados["transf_recebidas"]["atual"] = limpar(row[2])
                    dados["transf_recebidas"]["anterior"] = limpar(row[3])
                elif col_a == "REVERSíƒO DE PROVISí•ES E AJUSTES DE PERDAS":
                    dados["reversao_provisoes"]["atual"] = limpar(row[2])
                    dados["reversao_provisoes"]["anterior"] = limpar(row[3])
                if col_d == "VARIAí‡íƒO PATRIMONIAL DIMINUTIVA":
                    dados["variacoes_diminutivas"]["atual"] = limpar(row[6])
                    dados["variacoes_diminutivas"]["anterior"] = limpar(row[7])
                elif col_d == "PESSOAL E ENCARGOS":
                    dados["pessoal_encargos"]["atual"] = limpar(row[6])
                    dados["pessoal_encargos"]["anterior"] = limpar(row[7])
                elif col_d == "SERVIí‡OS TERCEIROS - PJ":
                    dados["servicos_terceiros"]["atual"] = limpar(row[6])
                    dados["servicos_terceiros"]["anterior"] = limpar(row[7])
                elif col_d == "TRANSFERíŠNCIAS E DELEGAí‡í•ES CONCEDIDAS":
                    dados["transf_concedidas"]["atual"] = limpar(row[6])
                    dados["transf_concedidas"]["anterior"] = limpar(row[7])
        # Calcula Superávit e Margem
        dados["superavit_patrimonial"]["atual"] = dados["variacoes_ativas"]["atual"] - dados["variacoes_diminutivas"]["atual"]
        dados["superavit_patrimonial"]["anterior"] = dados["variacoes_ativas"]["anterior"] - dados["variacoes_diminutivas"]["anterior"]
        if dados["variacoes_ativas"]["atual"] > 0:
            dados["margem_patrimonial"]["atual"] = (dados["superavit_patrimonial"]["atual"] / dados["variacoes_ativas"]["atual"]) * 100
        if dados["variacoes_ativas"]["anterior"] > 0:
            dados["margem_patrimonial"]["anterior"] = (dados["superavit_patrimonial"]["anterior"] / dados["variacoes_ativas"]["anterior"]) * 100
        return {"erro": False, "dados": dados}
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}
@app.get("/salvar_analise_patrimonial/{periodo}")
async def salvar_analise_patrimonial(periodo: str):
    try:
        dados = await api_analise_patrimonial(periodo)
        if dados.get("erro"): raise HTTPException(status_code=400, detail="Dados faltando")
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_patrimonial (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_analise_patrimonial (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados["dados"])))
        conn.commit()
        conn.close()
        return {"mensagem": "Salvo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/historico_analise_patrimonial")
async def listar_historico_patrimonial():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_patrimonial ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
async def listar_historico_patrimonial():
    return []
@app.get("/historico_analise_patrimonial/{id}")
async def buscar_historico_patrimonial(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_analise_patrimonial WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return {"periodo": row[0], "dados": json.loads(row[1])}
@app.delete("/excluir_analise_patrimonial/{id}")
async def excluir_historico_patrimonial(id: int):
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historico_analise_patrimonial WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return {"mensagem": "Excluido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/historico_composicao_rd/{id}")
async def buscar_historico_composicao_rd(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # A tabela pode ter colunas diferentes, vamos tentar resultado_json
    try:
        cursor.execute("SELECT periodo, resultado_json FROM historico_composicao_rd WHERE id = ?", (id,))
    except:
        # Se falhar, tenta sem o resultado_json
        cursor.execute("SELECT * FROM historico_composicao_rd WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    # Tenta pegar o periodo e o json
    periodo = row[0] if len(row) > 0 else "Desconhecido"
    dados_json = row[1] if len(row) > 1 else "{}"
    # Se dados_json for uma string, converte para dict
    if isinstance(dados_json, str):
        try: dados_json = json.loads(dados_json)
        except: dados_json = {}
    return {"periodo": periodo, "dados": dados_json}
@app.get("/gerar_pdf_analise_orcamentaria/{id}")
async def gerar_pdf_analise_orcamentaria(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json, sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, resultado_json FROM historico_analise_orcamentaria WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, d_json = row
        d = json.loads(d_json)
        # Estrutura esperada: { atual: {...}, anterior: {...} }
        a = d.get("atual", {})
        b = d.get("anterior", {})
        # --- 1. GERA O GRíFICO (Atual primeiro) ---
        labels = ["Receita Realizada", "Despesa Empenhada", "Superavit"]
        ant = [b.get("receita_realizada", 0), b.get("despesa_empenhada", 0), b.get("superavit", 0)]
        atu = [a.get("receita_realizada", 0), a.get("despesa_empenhada", 0), a.get("superavit", 0)]
        fig, ax = plt.subplots(figsize=(6, 2.8), dpi=150)
        x = range(len(labels))
        # Atual (azul escuro) na esquerda, Anterior (azul claro) na direita
        ax.bar([i - 0.2 for i in x], atu, width=0.4, label="Atual", color="#003366")
        ax.bar([i + 0.2 for i in x], ant, width=0.4, label="Anterior", color="#4a90e2")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10)
        ax.legend(loc="upper right", fontsize=9, frameon=False)
        formatter = ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:,.1f} Mi")
        ax.yaxis.set_major_formatter(formatter)
        ax.tick_params(axis="y", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_orc_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        # --- 2. MONTA O PDF ---
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Analise Orcamentaria Comparativa", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo de Referencia: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(8)
        # Tabela: Indicador | Periodo Atual | Periodo Anterior | Var (%)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 10)
        pdf.cell(80, 8, "Indicador", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 8, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 9)
        def fmt(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # Indicadores na ordem que queremos
        # Calcula os percentuais na hora para garantir precisão
        rec_orc = a.get("receita_orcada", 0) or 0
        rec_real = a.get("receita_realizada", 0) or 0
        desp_orc = a.get("despesa_orcada", 0) or 0
        desp_emp = a.get("despesa_empenhada", 0) or 0

        rec_orc_ant = b.get("receita_orcada", 0) or 0
        rec_real_ant = b.get("receita_realizada", 0) or 0
        desp_orc_ant = b.get("despesa_orcada", 0) or 0
        desp_emp_ant = b.get("despesa_empenhada", 0) or 0

        pct_rec = (rec_real / rec_orc * 100) if rec_orc else 0
        pct_desp = (desp_emp / desp_orc * 100) if desp_orc else 0

        pct_rec_ant = (rec_real_ant / rec_orc_ant * 100) if rec_orc_ant else 0
        pct_desp_ant = (desp_emp_ant / desp_orc_ant * 100) if desp_orc_ant else 0

        ind = [
            ("Receita Realizada", rec_real, rec_real_ant, 1e6),
            ("Despesas Empenhadas", desp_emp, desp_emp_ant, 1e6),
            ("Superavit Orcamentario", a.get("superavit", 0), b.get("superavit", 0), 1e6),
            ("Restos a Pagar Inscritos", a.get("restos_pagar", 0), b.get("restos_pagar", 0), 1e6),
            ("Receitas Orcadas", rec_orc, rec_orc_ant, 1e6),
            ("Despesas Orcadas", desp_orc, desp_orc_ant, 1e6),
            ("% de Realizacao das Receitas", pct_rec, pct_rec_ant, 1),
            ("% de Realizacao das Despesas", pct_desp, pct_desp_ant, 1),
        ]

        for nome, va, vb, m in ind:
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va) if m == 1e6 else f"{va:.2f}%", border=1, align="R")
            pdf.cell(45, 7, fmt(vb) if m == 1e6 else f"{vb:.2f}%", border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        # Grafico e Conclusao
        pdf.ln(8)
        y_atual = pdf.get_y()
        pdf.image(img_path, x=30, y=y_atual, w=110)
        # Conclusao no lado direito
        pdf.set_xy(150, y_atual)
        pdf.set_font(f_family, "B", 10)
        pdf.cell(0, 6, "Principais conclusoes:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(150)
        pdf.set_font(f_family, "", 8)
        txt_conclusao = f"A receita realizada representa {a.get('pct_receita', 0):.2f}% da previsao atualizada, enquanto as despesas empenhadas representam {a.get('pct_despesa', 0):.2f}% da dotacao atualizada."
        pdf.multi_cell(90, 4, txt_conclusao)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=analise_orcamentaria_{id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/gerar_pdf_analise_patrimonial/{id}")
async def gerar_pdf_analise_patrimonial(id: int):
    try:
        fonte_padrao = "Helvetica"
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from fastapi.responses import Response
        from app.routers.dvp import processar_dvp
        import sqlite3, os
        # 1. Busca o periodo no historico (ou usa fallback)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo FROM historico_analise_patrimonial WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        periodo = row[0] if row else "2026-TRIMESTRE-3"
        # 2. Calcula os dados do DVP
        p_limpo = periodo.replace("-", "_")
        caminho_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", f"DVP_{p_limpo}.csv")
        if not os.path.exists(caminho_csv):
            raise Exception(f"Arquivo DVP nao encontrado para {periodo}")
        resultado = processar_dvp(caminho_csv)
        d = resultado["dados"]
        # 3. Monta o PDF Moderno
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)
        # Cabecalho azul escuro
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_font(fonte_padrao, "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 8)
        pdf.cell(180, 10, "DVP - Demonstração das Variaçíµes Patrimoniais", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Perí­odo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Linha amarela
        pdf.set_draw_color(0, 51, 102)  # Linha azul (era amarela)
        pdf.set_line_width(1.5)
        pdf.line(0, 35, 210, 35)
        # Funcao para formatar valores
        def fmt_mi(v):
            try:
                s = f"R$ {v:,.2f}"
                return s.replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(v)
        # Cards de totais
        y_pos = 50
        card_w = 90
        card_h = 35
        # Card 1: Total VPA
        pdf.set_fill_color(232, 244, 248)
        pdf.rect(15, y_pos, card_w, card_h, "F")
        pdf.set_text_color(0, 51, 102)
        pdf.set_font(fonte_padrao, "B", 14)
        pdf.set_xy(20, y_pos + 5)
        pdf.cell(card_w, 10, fmt_mi(d['total_vpa']['atual']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(20, y_pos + 20)
        pdf.cell(card_w, 5, "Total VPA (Variaçíµes Aumentativas)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Card 2: Total VPD
        pdf.set_fill_color(248, 232, 232)
        pdf.rect(105, y_pos, card_w, card_h, "F")
        pdf.set_text_color(220, 53, 69)
        pdf.set_font(fonte_padrao, "B", 14)
        pdf.set_xy(110, y_pos + 5)
        pdf.cell(card_w, 10, fmt_mi(d['total_vpd']['atual']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(110, y_pos + 20)
        pdf.cell(card_w, 5, "Total VPD (Variaçíµes Diminutivas)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Card 3: Resultado
        y_pos += 45
        pdf.set_fill_color(238, 245, 232)
        pdf.rect(15, y_pos, 180, 40, "F")
        cor_res = (0, 51, 102) if d['resultado']['atual'] >= 0 else (220, 53, 69)
        pdf.set_text_color(*cor_res)
        pdf.set_font(fonte_padrao, "B", 12)
        pdf.set_xy(20, y_pos + 5)
        pdf.cell(180, 5, d['tipo_resultado']['atual'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "B", 24)
        pdf.set_xy(20, y_pos + 12)
        pdf.cell(180, 10, fmt_mi(d['resultado']['atual']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(20, y_pos + 28)
        pdf.cell(180, 5, "(Total VPA - Total VPD)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Tabela detalhada
        y_pos += 55
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.2)
        # Definir borda fina azul escuro
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.2)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, y_pos)
        pdf.cell(90, 8, "Indicador", border=1, fill=True)
        pdf.cell(40, 8, "Perí­odo Atual", border=1, fill=True, align="R")
        pdf.cell(40, 8, "Perí­odo Anterior", border=1, fill=True, align="R")
        pdf.ln()
        y_pos += 8
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(fonte_padrao, "", 9)
        def add_linha(nome, at, ant, bold=False):
            nonlocal y_pos
            if bold:
                pdf.set_font(fonte_padrao, "B", 9)
            else:
                pdf.set_font(fonte_padrao, "", 9)
            pdf.set_xy(15, y_pos)
            pdf.cell(90, 7, nome, border=1)
            pdf.cell(40, 7, f"R$ {fmt_mi(at)}", border=1, align="R")
            pdf.cell(40, 7, f"R$ {fmt_mi(ant)}", border=1, align="R")
            pdf.ln()
            y_pos += 6
        # Bloco VPA
        pdf.set_fill_color(232, 244, 248)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "VPA - VARIAí‡í•ES PATRIMONIAIS AUMENTATIVAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("VPA Financeiras", d['vpa_financeiras']['atual'], d['vpa_financeiras']['anterior'])
        add_linha("Transferíªncias Recebidas", d['transf_recebidas']['atual'], d['transf_recebidas']['anterior'])
        add_linha("Outras VPA", d['outras_vpa']['atual'], d['outras_vpa']['anterior'])
        add_linha("Reversão de Provisíµes", d['reversao_provisoes']['atual'], d['reversao_provisoes']['anterior'])
        add_linha("TOTAL VPA", d['total_vpa']['atual'], d['total_vpa']['anterior'], bold=True)
        # Bloco VPD
        pdf.set_fill_color(248, 232, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "VPD - VARIAí‡í•ES PATRIMONIAIS DIMINUTIVAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("VPD Financeiras", d['vpd_financeiras']['atual'], d['vpd_financeiras']['anterior'])
        add_linha("Pessoal e Encargos", d['pessoal_encargos']['atual'], d['pessoal_encargos']['anterior'])
        add_linha("Uso de Material de Consumo", d['uso_material_consumo']['atual'], d['uso_material_consumo']['anterior'])
        add_linha("Serviços", d['servicos']['atual'], d['servicos']['anterior'])
        add_linha("Depreciação", d['depreciacao']['atual'], d['depreciacao']['anterior'])
        add_linha("Amortização", d['amortizacao']['atual'], d['amortizacao']['anterior'])
        add_linha("Transferíªncias Concedidas", d['transf_concedidas']['atual'], d['transf_concedidas']['anterior'])
        add_linha("Outras VPD", d['outras_vpd']['atual'], d['outras_vpd']['anterior'])
        add_linha("Tributárias", d['tributarias']['atual'], d['tributarias']['anterior'])
        add_linha("TOTAL VPD", d['total_vpd']['atual'], d['total_vpd']['anterior'], bold=True)
        # Rodape
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(15, 285, 195, 285)
        pdf.set_text_color(120, 120, 120)
        pdf.set_font(fonte_padrao, "I", 8)
        pdf.set_xy(15, 287)
        pdf.cell(90, 5, "Cofen - Analise das Demonstracoes Contabeis", new_x=XPos.RIGHT, new_y=YPos.TOP)
        from datetime import datetime
        pdf.set_xy(135, 287)
        pdf.cell(60, 5, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", align="R")
        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=dvp_{periodo}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
@app.get("/gerar_pdf_composicao_receitas_despesas/{id}")
async def gerar_pdf_composicao_receitas_despesas(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json, sqlite3
        # 1. Busca o periodo e os dados no banco
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, resultado_json FROM historico_composicao_rd WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, d_json = row
        d = json.loads(d_json)
        # Estrutura esperada: { atual: { receitas: {...}, despesas: {...} }, anterior: { receitas: {...}, despesas: {...} } }
        a = d.get("atual", {})
        b = d.get("anterior", {})
        # 2. Prepara os dados para o gráfico (Receitas)
        labels = list(a.get("receitas", {}).keys())
        data_a = [a.get("receitas", {}).get(k, 0) for k in labels]
        data_b = [b.get("receitas", {}).get(k, 0) for k in labels]
        fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], data_a, width=0.4, label="Atual", color="#003366")
        ax.bar([i + 0.2 for i in x], data_b, width=0.4, label="Anterior", color="#4a90e2")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=15)
        ax.legend(loc="upper right", fontsize=8, frameon=False)
        formatter = ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:,.1f} Mi")
        ax.yaxis.set_major_formatter(formatter)
        ax.tick_params(axis="y", labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_comp_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        # 3. Monta o PDF
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Composicao de Receitas e Despesas", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)
        def fmt(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # --- Tabela de Receitas ---
        pdf.set_font(f_family, "B", 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, "RECEITAS (R$ mil)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 9)
        pdf.cell(80, 7, "Conta", border=1, fill=True, align="L")
        pdf.cell(45, 7, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 7, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 7, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 8)
        for k, va in a.get("receitas", {}).items():
            vb = b.get("receitas", {}).get(k, 0)
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 6, k, border=1, align="L")
            pdf.cell(45, 6, fmt(va), border=1, align="R")
            pdf.cell(45, 6, fmt(vb), border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 6, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        # --- Tabela de Despesas ---
        pdf.set_font(f_family, "B", 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, "DESPESAS (R$ mil)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 9)
        pdf.cell(80, 7, "Conta", border=1, fill=True, align="L")
        pdf.cell(45, 7, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 7, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 7, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 8)
        for k, va in a.get("despesas", {}).items():
            vb = b.get("despesas", {}).get(k, 0)
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 6, k, border=1, align="L")
            pdf.cell(45, 6, fmt(va), border=1, align="R")
            pdf.cell(45, 6, fmt(vb), border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 6, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        # 4. Adiciona o gráfico no final
        pdf.ln(8)
        pdf.image(img_path, x=40, y=pdf.get_y(), w=160)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=composicao_{id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/gerar_pdf_base_legal")
async def gerar_pdf_base_legal(periodo: str):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        # Tenta carregar a fonte Arial
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Base Legal e Metodologia", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo de Referencia: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        # --- LEGISLACAO E NORMAS APLICADAS (ATUALIZADO) ---
        pdf.set_font(f_family, "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Legislacao e Normas Aplicadas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(f_family, "", 10)
        normas = [
            "Lei no 4.320/1964",
            "Resolução Cofen nº 814/2026",
            "Manual de Contabilidade Aplicada ao Setor Publico (MCASP)",
            "Resolucao COFEN no 340/2008 (Regulamento da Administracao Financeira e Contabil)",
            "Resolucao COFEN no 764/2024 (Prestacao de Contas)",
            "Normas Brasileiras de Contabilidade - Setor Publico (NBC TSP)",
            "Resolucao COFEN no 814/2026 (Limites de Despesa com Pessoal e Governanca)"]
        for norma in normas:
            pdf.cell(0, 5, "- " + norma, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        # --- DEMONSTRACOES ANALISADAS ---
        pdf.set_font(f_family, "B", 12)
        pdf.cell(0, 8, "Demonstracoes Analisadas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(f_family, "", 10)
        demos = [
            "Balancete de Verificacao",
            "Balanco Financeiro (BF)",
            "Balanco Orcamentario (BO)",
            "Balanco Patrimonial (BP)",
            "Demonstracao do Fluxo de Caixa (DFC)",
            "Demonstracao das Mutacoes do PL (DMPL)",
            "Demonstracao das Variacoes Patrimoniais (DVP)"
        ]
        for demo in demos:
            pdf.cell(0, 5, "- " + demo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=base_legal_{periodo}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/custo_pessoal/{periodo}")
async def api_custo_pessoal(periodo: str, entidade: str = None):
    from matriz_integridade import _get_csv, _ler_linhas, _limpar_valor
    import re, os
    import sqlite3 as _sqlite3
    # Ler configuracao global
    if not entidade:
        _db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        _conn = _sqlite3.connect(_db_path)
        _cur = _conn.cursor()
        _cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        _row = _cur.fetchone()
        _conn.close()
        entidade = _row[0] if _row else "COFEN"
    print(f"[CUSTO PESSOAL] entidade={entidade}")
    def periodos_anteriores(p):
        partes = p.split("-")
        ano = int(partes[0]); tipo = partes[1]; valor = int(partes[2])
        meses_faltando = 12 - (valor * 3)
        periodos = []
        while meses_faltando > 0:
            if valor == 1: ano -= 1; valor = 4
            elif valor == 2: ano -= 1; valor = 4
            elif valor == 3: ano -= 1; valor = 4
            else: valor = 3
            periodos.append(f"{ano}-{tipo}-{valor}")
            meses_faltando -= 3
        return periodos
    periodos = [periodo] + periodos_anteriores(periodo)
    faltando = []
    for p in periodos:
        if not _get_csv("BALANCO_ORCAMENTARIO", p):
            faltando.append(f"BALANCO_ORCAMENTARIO ({p})")
    if faltando:
        return {"erro": "faltando", "pecas": faltando}
    def extrair_bo(p):
        caminho = _get_csv("BALANCO_ORCAMENTARIO", p)
        if not caminho:
            return None
        linhas = _ler_linhas(caminho)
        valores = {
            "pessoal": 0.0, "outras": 0.0, "terc": 0.0, "sent": 0.0,
            "receitas_realizadas": 0.0, "cota_parte": 0.0
        }
        # Para Pessoal, vamos pegar a linha com o MAIOR valor que contenha "PESSOAL E ENCARGOS SOCIAIS"
        maior_pessoal = 0.0
        maior_outras = 0.0
        maior_terc = 0.0
        maior_sent = 0.0
        for linha in linhas:
            if len(linha) < 7: continue
            nome = linha[0].strip().upper()
            # Receitas Correntes Realizadas
            if nome == "RECEITAS CORRENTE":
                if len(linha) >= 8:
                    valores["receitas_realizadas"] = _limpar_valor(linha[6])
                elif len(linha) >= 7:
                    valores["receitas_realizadas"] = _limpar_valor(linha[5])
            # Cota Parte
            if "COTA PARTE" in nome or "COTA-PARTE" in nome:
                if len(linha) >= 8:
                    valores["cota_parte"] = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    valores["cota_parte"] = _limpar_valor(linha[4])
            # Pessoal e Encargos Sociais - pega o maior valor
            if "PESSOAL E ENCARGOS SOCIAIS" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_pessoal:
                    maior_pessoal = val
            # Outras Despesas Variáveis - pega o maior valor
            if "OUTRAS DESPESAS VARI" in nome.upper() and ("PESSOAL" in nome.upper() or "RGPS" in nome.upper()):
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_outras:
                    maior_outras = val
            # Terceirização - pega o maior valor
            if "OUTRAS DESPESAS DE PESSOAL DECORRENTES" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_terc:
                    maior_terc = val
            # Sentenças Judiciais Trabalhistas - pega o maior valor
            if "SENTENí‡AS JUDICIAIS" in nome and "TRABALHISTAS" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_sent:
                    maior_sent = val
        valores["pessoal"] = maior_pessoal
        valores["outras"] = maior_outras
        valores["terc"] = maior_terc
        valores["sent"] = maior_sent
        return valores
    dados_atual = extrair_bo(periodo)
    dados_anteriores = [extrair_bo(p) for p in periodos_anteriores(periodo)]
    custo_atual = dados_atual["pessoal"] + dados_atual["outras"] + dados_atual["terc"] - dados_atual["sent"]
    custo_anterior = sum(d["pessoal"] + d["outras"] + d["terc"] - d["sent"] for d in dados_anteriores)
    rcl_atual = dados_atual["receitas_realizadas"] - dados_atual["cota_parte"]
    rcl_anterior = sum(d["receitas_realizadas"] - d["cota_parte"] for d in dados_anteriores)
    # Lí³gica de Faixas de Controle (Art. 6Âº da Resolução Cofen 814/2026)
    pct_custo_total = ((custo_atual + custo_anterior) / (rcl_atual + rcl_anterior)) * 100 if (rcl_atual + rcl_anterior) > 0 else 0
    is_coren = (entidade.upper() == "COREN")

    if is_coren:
        if pct_custo_total > 60:
            faixa, cor = "Faixa Crí­tica (> 60%)", "danger"
        elif pct_custo_total >= 57:
            faixa, cor = "Faixa Prudencial (57% a 60%)", "warning"
        elif pct_custo_total >= 54:
            faixa, cor = "Faixa de Alerta (54% a 57%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"
    else:
        if pct_custo_total > 50:
            faixa, cor = "Faixa Crí­tica (> 50%)", "danger"
        elif pct_custo_total >= 47.5:
            faixa, cor = "Faixa Prudencial (47,5% a 50%)", "warning"
        elif pct_custo_total >= 45:
            faixa, cor = "Faixa de Alerta (45% a 47,5%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"

    return {
        "erro": False,
        "rcl_atual": rcl_atual,
        "rcl_anterior": rcl_anterior,
        "rcl_total": rcl_atual + rcl_anterior,
        "pessoal_atual": dados_atual["pessoal"],
        "pessoal_anterior": sum(d["pessoal"] for d in dados_anteriores),
        "pessoal_total": dados_atual["pessoal"] + sum(d["pessoal"] for d in dados_anteriores),
        "outras_atual": dados_atual["outras"],
        "outras_anterior": sum(d["outras"] for d in dados_anteriores),
        "outras_total": dados_atual["outras"] + sum(d["outras"] for d in dados_anteriores),
        "terc_atual": dados_atual["terc"],
        "terc_anterior": sum(d["terc"] for d in dados_anteriores),
        "terc_total": dados_atual["terc"] + sum(d["terc"] for d in dados_anteriores),
        "custo_atual": custo_atual,
        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_total": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "limite_atual": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),
        "custo_anterior": custo_anterior,
        "custo_total": custo_atual + custo_anterior,
        "faixa_controle": faixa,
        "faixa_cor": cor,
        "pct_custo_total": pct_custo_total
    }
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_custo_pessoal ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_custo_pessoal/{id}")
async def buscar_historico_custo_pessoal(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_custo_pessoal WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return {"periodo": row[0], "dados": json.loads(row[1])}
@app.delete("/excluir_custo_pessoal/{id}")
async def excluir_historico_custo_pessoal(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_custo_pessoal WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}
@app.get("/analise_orcamentaria")
async def serve_analise_orcamentaria():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_orcamentaria.html")
    return FileResponse(caminho)
@app.get("/api/relatorios_importados")
async def api_relatorios_importados():
    import os, glob
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    arquivos = glob.glob(os.path.join(pasta, "*.csv"))
    lista = []
    for arq in arquivos:
        if os.path.exists(arq):
            nome = os.path.basename(arq)
            partes = nome.replace(".csv", "").split("_")
            tipo = partes[0] if partes else "Desconhecido"
            periodo = "Não identificado"
            for i, p in enumerate(partes):
                if len(p) == 4 and p.isdigit():
                    if i + 2 < len(partes):
                        periodo = f"{p} - {partes[i+1]} {partes[i+2]}"
                    else:
                        periodo = p
                    break
            lista.append({"nome": nome, "tipo": tipo, "periodo": periodo})
    lista.sort(key=lambda x: x["nome"])
    return lista
@app.get("/base_legal")
async def serve_base_legal():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "base_legal.html")
    return FileResponse(caminho)
@app.get("/salvar_base_legal/{periodo}")
async def salvar_base_legal(periodo: str, periodo_anterior: str = "2025-TRIMESTRE-3"):
    try:
        import sqlite3, json, datetime, os
        # Simulamos o salvamento dos dados do Base Legal (que são fixos, mas dependem do perí­odo)
        # O PDF será gerado posteriormente com base no ID salvo
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_base_legal (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, periodo_anterior TEXT, data_geracao TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_base_legal (periodo, periodo_anterior, data_geracao) VALUES (?, ?, ?)",
                       (periodo, periodo_anterior, data_agora))
        conn.commit()
        conn.close()
        return {"mensagem": "Base Legal salva!", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/historico_base_legal")
async def listar_base_legal():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, periodo_anterior, data_geracao FROM historico_base_legal ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "periodo_anterior": r[2], "data_geracao": r[3]} for r in rows]
@app.get("/liquidez")
async def serve_liquidez():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "liquidez.html")
    return FileResponse(caminho)
def _calc_liquidez(periodo):
    """Calcula indices de liquidez/estrutura para exercicio ATUAL e ANTERIOR."""
    from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
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


def demonstracoes_em_breve():
    return HTMLResponse(content="<html><body><h1>Demonstraçíµes Contábeis</h1><p>Em breve.</p><a href='/'>Voltar</a></body></html>")
@app.get("/analises", response_class=HTMLResponse)
def analises_em_breve():
    return HTMLResponse(content="<html><body><h1>Análises Contábeis</h1><p>Em breve.</p><a href='/'>Voltar</a></body></html>")
@app.post("/salvar_custo_pessoal/{periodo}")
def salvar_custo_pessoal_rota(periodo: str):
    import sqlite3, json, os, datetime
    try:
        # Chama a função de cálculo diretamente
        from main import api_custo_pessoal
        import asyncio
        dados = asyncio.run(api_custo_pessoal(periodo))
        if isinstance(dados, dict) and dados.get("erro"):
            return {"erro": True, "mensagem": str(dados.get("erro"))}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_custo_pessoal (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        # SEMPRE INSERE (nunca sobrescreve)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_custo_pessoal (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": "Relatí³rio salvo!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
# === ROUTER DO PANORAMA (registrado por ultimo para vencer a rota antiga) ===
from app.routers.panorama import router as panorama_router
app.include_router(panorama_router)
# === ROUTER DO DVP ===
from app.routers.dvp import router as dvp_router
app.include_router(dvp_router)
# === ROUTER DO BALANCO FINANCEIRO ===
from app.routers.balanco_financeiro import router as bf_router
app.include_router(bf_router)
@app.get("/custo_pessoal_pdf_completo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_completo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_completo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = _corrigir_encoding(f.read())
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
@app.get("/custo_pessoal_pdf_resumo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_resumo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_resumo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = _corrigir_encoding(f.read())
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF RESUMO] Historico ID {id} -> periodo {periodo}")
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        conn.close()
        print(f"[PDF RESUMO] periodo={periodo}, entidade={entidade}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9994/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_resumo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF RESUMO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)
@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF COMPLETO] Historico ID {id} -> periodo {periodo}")
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        conn.close()
        print(f"[PDF COMPLETO] periodo={periodo}, entidade={entidade}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9994/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_completo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF COMPLETO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)
@app.get("/analise_custo_pessoal", response_class=HTMLResponse)
def serve_analise_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse(content="<h1>Arquivo analise_custo_pessoal.html não encontrado!</h1>", status_code=404)
@app.get("/historico_custo_pessoal")
async def listar_historico_custo_pessoal():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, periodo, data_geracao FROM historico_custo_pessoal ORDER BY id DESC")
        rows = cur.fetchall()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    finally:
        conn.close()
@app.get("/api/configuracoes/custo_pessoal")
def api_configuracoes_custo_pessoal_get():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        row = cur.fetchone()
        conn.close()
        entidade = row[0] if row else "COFEN"
        return {"tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
@app.post("/api/configuracoes/custo_pessoal")
async def api_configuracoes_custo_pessoal_post(request: Request):
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        dados = await request.json()
        entidade = dados.get("tipo_entidade", "COFEN").upper()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('tipo_entidade', ?)", (entidade,))
        conn.commit()
        conn.close()
        return {"ok": True, "tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
@app.get("/configuracoes_custo_pessoal", response_class=HTMLResponse)
def serve_configuracoes_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "configuracoes_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Arquivo de configuraçíµes não encontrado</h1>", status_code=404)


@app.get("/analise_centro_custos", response_class=HTMLResponse)
def serve_analise_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)


@app.get("/historico_centro_custos")
def get_historico_centro_custos():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_centro_custos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_centro_custos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_centro_custos/{id}")
def get_historico_centro_custos_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_centro_custos WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_centro_custos")
async def salvar_centro_custos(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/historico_centro_custos/{id}")
def excluir_historico_centro_custos(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_centro_custos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.post("/excluir_multiplos_custo_pessoal")
async def excluir_multiplos_custo_pessoal(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Monta a query com placeholders para evitar SQL Injection
    placeholders = ",".join(["?"] * len(ids))
    cursor.execute(f"DELETE FROM historico_custo_pessoal WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cursor.rowcount
    conn.close()

    return {"ok": True, "excluidos": excluidos}


@app.post("/api/centro_custos/importar")
async def importar_centro_custos(file: UploadFile = File(...)):
    import csv, io
    try:
        # Líª o conteíºdo do arquivo
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # Remove BOM se houver
        reader = csv.DictReader(io.StringIO(decoded))

        centros = []
        for row in reader:
            # Tenta encontrar as colunas (aceita variaçíµes de nome)
            nome = row.get("Centro de Custo") or row.get("centro_custo") or row.get("Nome") or row.get("nome") or ""
            valor_str = row.get("Valor") or row.get("valor") or row.get("Valor (R$)") or "0"

            # Limpa o valor (troca ví­rgula por ponto e remove R$)
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


@app.get("/api/relatorio_centro_custos")
def api_relatorio_centro_custos(id: int = None, periodo: str = "2026-TRIMESTRE-3", periodo_anterior: str = None):
    import sqlite3, os, json, csv, io

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Calcula o perí­odo anterior automaticamente (mesmo trimestre do ano anterior)
    if not periodo_anterior:
        partes = periodo.split("-")
        if len(partes) == 3:
            ano = int(partes[0])
            tipo = partes[1]
            valor = partes[2]
            periodo_anterior = f"{ano - 1}-{tipo}-{valor}"

    def ler_csv(periodo_str):
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return []

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            # Encontra o iní­cio dos dados reais (primeira linha que começa com "01 - AF")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                linha_limpa = linha.strip().strip('"')
                if linha_limpa.startswith("01 - AF") or linha_limpa.startswith("1 - AF"):
                    inicio_dados = i
                    break

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

            return centros
        except:
            return []

    def buscar_historico(periodo_str):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo_str,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def processar(centros, periodo_str):
        if not centros:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}}

        total = sum(c.get("valor", 0) for c in centros)

        meses = {}
        if total > 0:
            meses = {
                "JAN": total * 0.12,
                "FEV": total * 0.13,
                "MAR": total * 0.20,
                "ABR": total * 0.15,
                "MAI": total * 0.20,
                "JUN": total * 0.20
            }

        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
            "meses": meses
        }

    centros_atual = ler_csv(periodo)
    if not centros_atual:
        dados_banco = buscar_historico(periodo)
        if dados_banco:
            centros_atual = dados_banco.get("centros", [])

    centros_anterior = ler_csv(periodo_anterior)
    if not centros_anterior:
        dados_banco_anterior = buscar_historico(periodo_anterior)
        if dados_banco_anterior:
            centros_anterior = dados_banco_anterior.get("centros", [])

    conn.close()

    atual = processar(centros_atual, periodo)
    anterior = processar(centros_anterior, periodo_anterior) if centros_anterior else None

    if anterior is None or anterior["total"] == 0:
        return {
            "periodo": periodo,
            "periodo_anterior": periodo_anterior,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o perí­odo anterior."
        }

    return {
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
@app.get("/relatorio_centro_custos", response_class=HTMLResponse)
def serve_relatorio_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.get("/relatorio_centro_custos_completo", response_class=HTMLResponse)
def serve_relatorio_centro_custos_completo():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.post("/excluir_multiplos_centro_custos")
async def excluir_multiplos_centro_custos(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(ids))
    cursor.execute(f"DELETE FROM historico_centro_custos WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cursor.rowcount
    conn.close()

    return {"ok": True, "excluidos": excluidos}


@app.get("/api/centro_custos/{periodo}")
def api_centro_custos(periodo: str):
    import os, csv, io

    def ler_csv(periodo_str):
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
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
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            # Encontra o iní­cio dos dados reais (primeira linha que começa com "01 - AF")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                linha_limpa = linha.strip().strip('"')
                if linha_limpa.startswith("01 - AF") or linha_limpa.startswith("1 - AF"):
                    inicio_dados = i
                    break

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

            return centros
        except Exception as e:
            return None

    # Líª o perí­odo atual
    centros_atual = ler_csv(periodo)
    if centros_atual is None:
        return {"erro": True, "mensagem": f"Arquivo para o perí­odo {periodo} não encontrado."}

    # Calcula o perí­odo anterior (mesmo trimestre/míªs do ano anterior)
    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior_str = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior_str = None

    centros_anterior = ler_csv(periodo_anterior_str) if periodo_anterior_str else None

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior_str,
        "centros": centros_atual,
        "centros_anterior": centros_anterior if centros_anterior else []
    }


@app.get("/api/relatorio_v2/{periodo}")
def api_relatorio_v2(periodo: str):
    import sqlite3, os, json, csv, io

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    # Calcula o perí­odo anterior (mesmo trimestre do ano anterior)
    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    def ler_csv(periodo_str):
        if not periodo_str:
            return []
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return []

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break

            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1

            # Líª o cabeçalho para descobrir os meses
            meses_disponiveis = []
            for i in range(max(0, inicio_dados - 5), inicio_dados):
                if "JAN" in linhas[i].upper():
                    if ";" in linhas[i]:
                        partes_cab = linhas[i].strip().split(";")
                    else:
                        partes_cab = linhas[i].strip().split(",")
                    for p in partes_cab:
                        p_limpo = p.strip().upper()
                        if p_limpo in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]:
                            meses_disponiveis.append(p_limpo)
                    break

            if not meses_disponiveis:
                meses_disponiveis = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET"]

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

                # Valor total (íºltima coluna)
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

            # Calcula os meses por centro
            meses_por_centro = []
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

                valores_meses = []
                for idx, mes in enumerate(meses_disponiveis, start=1):
                    if idx < len(partes):
                        v_str = partes[idx].strip().strip('"').replace(".", "").replace(",", ".")
                        try:
                            v = float(v_str)
                        except:
                            v = 0.0
                    else:
                        v = 0.0
                    valores_meses.append(v)

                meses_por_centro.append({"nome": nome, "meses": valores_meses})

            return {"centros": centros, "meses": meses_disponiveis, "meses_por_centro": meses_por_centro}
        except:
            return {"centros": [], "meses": [], "meses_por_centro": []}

    dados_atual = ler_csv(periodo)
    dados_anterior = ler_csv(periodo_anterior)

    def processar(dados):
        if not dados or not dados.get("centros"):
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}

        centros = dados["centros"]
        total = sum(c.get("valor", 0) for c in centros)
        meses = dados["meses"]
        meses_por_centro = dados.get("meses_por_centro", [])

        # Calcula os totais mensais
        totais_meses = {m: 0.0 for m in meses}
        for item in meses_por_centro:
            for idx, m in enumerate(meses):
                if idx < len(item["meses"]):
                    totais_meses[m] += item["meses"][idx]

        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / len(meses) if meses and total > 0 else 0,
            "meses": totais_meses,
            "meses_disponiveis": meses
        }

    atual = processar(dados_atual)
    anterior = processar(dados_anterior) if dados_anterior and dados_anterior.get("centros") else {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}

    return {
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
@app.get("/relatorio_centro_custos_v2", response_class=HTMLResponse)
def serve_relatorio_v2():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos_v2.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.post("/salvar_relatorio_v2")
async def salvar_relatorio_v2(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo")
    texto_total = dados.get("texto_total")
    texto_concentracao = dados.get("texto_concentracao")
    texto_alertas = dados.get("texto_alertas")
    texto_recomendacoes = dados.get("texto_recomendacoes")

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS relatorio_v2_salvo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, texto_total TEXT,
        texto_concentracao TEXT, texto_alertas TEXT, texto_recomendacoes TEXT, data_edicao TEXT)""")

    data_edicao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("""INSERT INTO relatorio_v2_salvo
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao))
    conn.commit()
    conn.close()
    return {"ok": True, "id": cur.lastrowid}


@app.get("/relatorio_final", response_class=HTMLResponse)
def serve_relatorio_final():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


# ========== ROTAS DO COMPARATIVO DE RECEITAS ==========
@app.get("/api/comparativo_receitas/{periodo}")
def api_comparativo_receitas(periodo: str):
    import os, csv, io
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    # Simulação: retorna dados fictí­cios de receitas (adapte para ler o CSV real, se houver)
    receitas = [
        {"nome": "Receita de Serviços", "valor": 120000000.0},
        {"nome": "Receitas Financeiras", "valor": 25000000.0},
        {"nome": "Outras Receitas", "valor": 12000000.0}
    ]
    return {"erro": False, "periodo": periodo, "receitas": receitas}

@app.get("/historico_comparativo_receitas")
def get_historico_comparativo_receitas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_receitas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_receitas/{id}")
def get_historico_comparativo_receitas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_receitas WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_receitas")
async def salvar_comparativo_receitas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False, "mensagem": "Nenhum ID."}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cur.rowcount
    conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_receitas", response_class=HTMLResponse)
def serve_analise_comparativo_receitas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_receitas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)

@app.get("/relatorio_comparativo_receitas", response_class=HTMLResponse)
def serve_relatorio_comparativo_receitas():
    # Por enquanto, redireciona para o relatí³rio de centro de custos (ou crie um novo HTML)
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.get("/api/comparativo_receitas_v2/{periodo}")
def api_comparativo_receitas_v2(periodo: str):
    import os, re

    upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"

    # Calcula o perí­odo anterior (mesmo trimestre do ano anterior)
    partes = periodo.split("-")
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

            grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERíŠNCIAS CORRENTES", "RECEITAS DE SERVIí‡OS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIí‡í•ES"]

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

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": "Dados não encontrados para o perí­odo atual."}

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {"orcado_total": 0, "realizado_total": 0, "percentual_total": 0, "grupos": [], "cores": []}
    }


@app.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os

    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo={periodo}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)  # Espera gráficos renderizarem
        page.evaluate("""() => {
            document.querySelectorAll('canvas').forEach(canvas => {
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.className = 'canvas-img';
                img.style.cssText = 'display: block; max-width: 100%; max-height: 240px; margin: 0 auto;';
                canvas.parentNode.insertBefore(img, canvas.nextSibling);
            });
        }""")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_receitas_{periodo}.pdf"}
    )


# ========== ROTAS DO COMPARATIVO DE DESPESAS ==========
@app.get("/api/comparativo_despesas_v2/{periodo}")
def api_comparativo_despesas_v2(periodo: str):
    import os, unicodedata
    upload_dir = r"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\uploads_raw"

    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0

    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0

    def normalizar(txt):
        return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8').strip().upper()

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

            # Lista fixa de cabeçalhos que NíƒO são contas analí­ticas
            cabecalhos = [
                "CREDITO DISPONIVEL", "CREDITO DISPONIVEL - DESPESA CORRENTE",
                "CREDITO DISPONIVEL - DESPESA CAPITAL",
                "PESSOAL E ENCARGOS SOCIAIS", "JUROS E ENCARGOS DA DIVIDA",
                "OUTRAS DESPESAS CORRENTES", "INVESTIMENTOS",
                "INVERSOES FINANCEIRAS", "AMORTIZACAO DA DIVIDA",
                "APLICACOES DIRETAS", "APLICACOES INDIRETAS",
                "OUTROS SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "DEMAIS SERVICOS - PESSOAS JURIDICAS",
                "APOSENTADORIAS DO RPPS", "PROVENTOS - PESSOAL CIVIL",
                "VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL",
                "OUTRAS DESPESAS VARIAVEIS - PESSOAL CIVIL - RGPS",
                "RESSARCIMENTO DE DESPESAS DE PESSOAL REQUISITADO",
                "JUROS SOBRE A DIVIDA POR CONTRATO",
                "JUROS DE SOBRE FORNECIMENTO DE BENS",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA FISICA",
                "OUTROS JUROS E ENCARGOS DE MORA",
                "DESPESAS DE EXERCICIOS ANTERIORES (JUROS E ENCARGOS DAS DIVIDAS)",
                "OUTRAS DESPESAS DE PESSOAL DECORRENTES DE CONTRATOS DE TERCEIROS",
                "OUTRAS DESPESAS CORRENTES - APLICACOES DIRETAS",
                "INVESTIMENTOS - APLICACOES DIRETAS",
                "INVERSOES FINANCEIRAS - APLICACOES DIRETAS",
                "AMORTIZACAO DA DIVIDA - APLICACOES DIRETAS",
                "TOTAL", "TOTAL GERAL"
            ]
            cabecalhos_norm = [normalizar(cg) for cg in cabecalhos]

            detalhes_temp = []

            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue

                nome_original = partes_linha[0].strip().strip('"')
                nome_norm = normalizar(nome_original)

                if not nome_original or len(nome_original) < 3: continue

                # Total Global
                if nome_norm == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])

                # Grupos contábeis
                grupos_alvo_norm = [
                    "PESSOAL E ENCARGOS SOCIAIS",
                    "JUROS E ENCARGOS DA DIVIDA",
                    "OUTRAS DESPESAS CORRENTES",
                    "INVESTIMENTOS",
                    "INVERSOES FINANCEIRAS",
                    "AMORTIZACAO DA DIVIDA"
                ]
                if nome_norm in grupos_alvo_norm:
                    if not any(g["nome"] == nome_original for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })

                # Detalhes: exclui cabeçalhos e pega o resto com valor > 0
                valor_emp = parse_valor(partes_linha[2])
                if valor_emp > 0 and nome_norm not in cabecalhos_norm:
                    # Exclui também linhas com "TOTAL" no nome (são somatí³rios)
                    if "TOTAL" not in nome_norm and "SUBTOTAL" not in nome_norm:
                        detalhes_temp.append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": valor_emp,
                            "percentual": parse_pct(partes_linha[3])
                        })

            # Ordena por empenhado desc e pega top 10
            detalhes_temp.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = detalhes_temp[:10]

            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": [], "detalhes": []
        }
    }
@app.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_despesas ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_despesas/{id}")
def get_historico_comparativo_despesas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_despesas WHERE id = ?", (id,))
    row = cur.fetchone(); conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_despesas")
async def salvar_comparativo_despesas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit(); conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
    conn.commit(); excluidos = cur.rowcount; conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_despesas", response_class=HTMLResponse)
def serve_analise_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)


@app.get("/gerar_pdf_integridade_matriz/{check_id}")
def gerar_pdf_integridade_matriz(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela de integridade com o ID passado
    url = f"http://127.0.0.1:9994/integridade?check={check_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=integridade_{check_id}.pdf"}
    )


@app.get("/gerar_pdf_conferencia/{check_id}")
def gerar_pdf_conferencia(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela de conferíªncia com o ID passado
    url = f"http://127.0.0.1:9994/conferencia_nova?check={check_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=conferencia_{check_id}.pdf"}
    )


@app.get("/gerar_pdf_comparativo_despesas")
def gerar_pdf_comparativo_despesas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo={periodo}&_t={int(time.time())}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_despesas_{periodo}.pdf"})


@app.get("/relatorio_comparativo_despesas", response_class=HTMLResponse)
def serve_relatorio_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


# ========== ROTAS DE HISTí“RICO DESPESAS (FORí‡ADAS) ==========
@app.post("/api/comparativo_despesas_v2/{periodo}/salvar")
def rota_salvar_comparativo_despesas(periodo: str):
    import sqlite3, os, json
    from datetime import datetime

    dados = api_comparativo_despesas_v2(periodo)
    if dados.get("erro"): return {"erro": True, "mensagem": dados.get("mensagem")}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)

    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}

@app.delete("/historico_comparativo_despesas/{id}")
def rota_excluir_comparativo_despesas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_despesas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}
# ============================================================

@app.get("/gerar_pdf_composicao_receitas_despesas/{historico_id}")
def gerar_pdf_composicao_receitas_despesas(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela do relatí³rio passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_composicao_receitas_despesas?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=composicao_{historico_id}.pdf"}
    )

@app.get("/gerar_pdf_panorama/{historico_id}")
def gerar_pdf_panorama(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela do panorama passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000) # Espera extra para gráficos renderizarem
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=panorama_{historico_id}.pdf"}
    )

@app.get("/relatorio_panorama")
def serve_relatorio_panorama():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "relatorio_panorama.html")
    return FileResponse(caminho)

@app.get("/gerar_pdf_centro_custos/{historico_id}")
def gerar_pdf_centro_custos(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre o relatí³rio v2 passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_centro_custos?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=centro_custos_{historico_id}.pdf"}
    )

@app.post("/salvar_conclusao_centro_custos/{historico_id}")
async def salvar_conclusao_centro_custos(historico_id: int, request: Request):
    import sqlite3, json, os
    try:
        data = await request.json()
        texto = data.get("texto", "")

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE id = ?", (historico_id,))
        row = cur.fetchone()

        if row:
            dados = json.loads(row[0])
            dados["conclusao_personalizada"] = texto
            cur.execute("UPDATE historico_centro_custos SET dados_json = ? WHERE id = ?", (json.dumps(dados), historico_id))
            conn.commit()
            conn.close()
            return {"erro": False, "mensagem": "Conclusão salva com sucesso!"}

        conn.close()
        return {"erro": True, "mensagem": "Histí³rico não encontrado."}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.get("/relatorio_comparativo_receitas_v2")
def serve_relatorio_receitas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Tenta v2, senão a versão sem v2
    for nome in ["relatorio_comparativo_receitas_v2.html", "relatorio_comparativo_receitas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatí³rio não encontrado"}


# ============================================================
# ROTAS DE SALVAR E EXCLUIR - COMPARATIVO DE RECEITAS
# ============================================================

@app.post("/api/comparativo_receitas_v2/{periodo}/salvar")
def salvar_comparativo_receitas(periodo: str):
    import sqlite3, os, json
    from datetime import datetime

    # Pega os dados atuais via API
    try:
        dados = api_comparativo_receitas_v2(periodo)
    except Exception as e:
        return {"erro": True, "mensagem": f"Erro ao buscar dados: {str(e)}"}

    if dados.get("erro"):
        return {"erro": True, "mensagem": dados.get("mensagem", "Dados não encontrados")}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)

    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)",
                (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}


@app.delete("/historico_comparativo_receitas/{id}")
def excluir_historico_receitas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_receitas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}


@app.get("/relatorio_comparativo_despesas_v2")
def serve_relatorio_despesas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Procura o _v2 primeiro, senão o sem _v2
    for nome in ["relatorio_comparativo_despesas_v2.html", "relatorio_comparativo_despesas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatorio nao encontrado"}

@app.get("/download/pdf_csv/{tipo}")
async def download_pdf_csv(tipo: str, ano: int = Query(2026), periodo: str = Query("")):
    from fpdf import FPDF
    from fastapi.responses import Response
    import os

    # Mapeia o tipo para o nome do arquivo
    mapa = {
        "COMPARATIVO_DESPESAS": "COMPARATIVO_DESPESAS",
        "COMPARATIVO_RECEITAS": "COMPARATIVO_RECEITAS",
        "CENTRO_CUSTOS": "CENTRO_CUSTOS"
    }

    prefixo = mapa.get(tipo.upper(), tipo.upper())
    # Procura o arquivo mais recente com esse prefixo
    pasta = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
    arquivo = None
    for f in sorted(os.listdir(pasta), reverse=True):
        if f.startswith(prefixo) and f.endswith(".csv"):
            arquivo = os.path.join(pasta, f)
            break

    if not arquivo:
        return {"erro": True, "mensagem": f"Arquivo CSV para {tipo} não encontrado."}

    # Líª o CSV
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except:
        with open(arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()

    # Gera o PDF
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Tí­tulo
    pdf.set_font("Helvetica", "B", 16)
    titulo = tipo.replace("_", " ").title()
    pdf.cell(0, 10, f"Relatí³rio - {titulo}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Arquivo: {os.path.basename(arquivo)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Cabeçalho da tabela
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(0, 114, 186)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "Descrição", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Orçado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Realizado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "%", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    # Dados (pula linhas de cabeçalho)
    count = 0
    for linha in linhas:
        if ";" not in linha: continue
        partes = linha.strip().split(";")
        if len(partes) < 3: continue
        nome = partes[0].strip().strip('"')[:50]
        if not nome or "COFEN" in nome.upper() or "PERIODO" in nome.upper(): continue
        orcado = partes[1].strip() if len(partes) > 1 else ""
        realizado = partes[2].strip() if len(partes) > 2 else ""
        pct = partes[3].strip() if len(partes) > 3 else ""
        if not orcado or orcado == "Orçado": continue

        pdf.set_font("Helvetica", "", 7)
        pdf.cell(80, 6, nome, border=1)
        pdf.cell(30, 6, orcado, border=1, align="R")
        pdf.cell(30, 6, realizado, border=1, align="R")
        pdf.cell(30, 6, pct, border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        count += 1
        if count > 60: break

    out = pdf.output()
    return Response(content=bytes(out), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="relatorio_{tipo}_{ano}.pdf"'})


# ============================================================
# ROTAS DE CONFIGURACOES (CADASTRO DA ENTIDADE)
# ============================================================

@app.get('/api/configuracoes/entidade')
async def obter_entidade():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
    cursor = conn.cursor()

    # Cria a tabela se nao existir
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()

    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"razao_social": "", "nome_fantasia": "", "cnpj": "", "endereco": "", "email": "", "telefone": "", "contador_nome": "", "contador_crc": "", "contador_uf": "", "contador_cpf": "", "contador_email": "", "logo_path": ""}

    # Acessa pelo nome da coluna (evita erro de indice desalinhado)
    def get_col(nome):
        try:
            return row[nome] or ""
        except Exception:
            return ""

    return {
        "razao_social": get_col("razao_social"),
        "nome_fantasia": get_col("nome_fantasia"),
        "cnpj": get_col("cnpj"),
        "endereco": get_col("endereco"),
        "email": get_col("email"),
        "telefone": get_col("telefone"),
        "contador_nome": get_col("contador_nome"),
        "contador_crc": get_col("contador_crc"),
        "contador_uf": get_col("contador_uf"),
        "contador_cpf": get_col("contador_cpf"),
        "contador_email": get_col("contador_email"),
        "logo_path": get_col("logo_path")
    }

@app.post('/api/configuracoes/entidade')
async def salvar_entidade(request: Request):
    import sqlite3
    from datetime import datetime
    try:
        body = await request.json()
    except Exception:
        return {'ok': False, 'mensagem': 'Dados invalidos.'}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pc_storage', 'banco_dados.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT)''')
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('DELETE FROM configuracoes_entidade')
    cursor.execute('''INSERT INTO configuracoes_entidade
        (razao_social, nome_fantasia, cnpj, endereco, email, telefone, contador_nome, contador_crc, contador_uf, contador_cpf, contador_email, data_atualizacao, logo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        body.get('razao_social', ''),
        body.get('nome_fantasia', ''),
        body.get('cnpj', ''),
        body.get('endereco', ''),
        body.get('email', ''),
        body.get('telefone', ''),
        body.get('contador_nome', ''),
        body.get('contador_crc', ''),
        body.get('contador_uf', ''),
        body.get('contador_cpf', ''),
        body.get('contador_email', ''),
        data_agora,
        body.get('logo_path', '')))
    conn.commit()
    conn.close()
    return {'ok': True, 'mensagem': 'Configuracoes salvas com sucesso!'}

@app.get('/configuracoes')
async def serve_configuracoes():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pc_frontend', 'configuracoes.html')
    return FileResponse(caminho, headers={'Cache-Control': 'no-store, no-cache, must-revalidate'})


@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        msg = "Coluna logo_path adicionada."
    except Exception as e:
        msg = f"Ja existe ou erro: {str(e)[:50]}"
    conn.close()
    return {"ok": True, "mensagem": msg}


@app.post("/api/configuracoes/logo")
async def upload_logo(file: UploadFile = File(...)):
    import os, uuid, sqlite3
    from fastapi import HTTPException

    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PNG ou JPG.")

    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)

    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(await file.read())

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()

    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    cursor.execute("SELECT COUNT(*) FROM configuracoes_entidade")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', ?)", (nome_arquivo,))
    else:
        cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (nome_arquivo,))
    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}

@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        msg = "Coluna logo_path adicionada."
    except Exception as e:
        msg = "Coluna ja existe ou erro: " + str(e)[:50]
    conn.close()
    return {"ok": True, "mensagem": msg}


app.mount("/static_logos", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")), name="static_logos")


# ============================================================
# ROTAS DO RELATORIO CONSOLIDADO
# ============================================================


@app.get("/historico_relatorio_consolidado")
async def get_hist_consolidado():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_relatorio_consolidado ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.delete("/excluir_relatorio_consolidado/{id}")
async def excluir_relatorio_consolidado(id: int):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/relatorio_consolidado")
async def serve_relatorio_consolidado():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})


# ============================================================
# API DA ANALISE BP (Balanco Patrimonial)
# ============================================================


@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob, unicodedata
    from fastapi import HTTPException

    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    ano_atual = p_limpo.split("_")[0]
    candidatos = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_atual}*.csv"))
    if not candidatos:
        return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    caminho = candidatos[0]

    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").replace("C", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0

    def remover_acentos(s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').upper().strip()

    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            for row in csv.reader(f, delimiter=";"):
                linhas.append(row)

        # Ativo: Col0 (esp), Col1 (atual), Col2 (anterior)
        # Passivo: Col3 (esp), Col4 (atual), Col5 (anterior)

        def buscar_ativo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 2 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1]), limpar(p[2])
            return 0.0, 0.0

        def buscar_passivo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 5 and termo_norm in remover_acentos(str(p[3])):
                    return limpar(p[4]), limpar(p[5])
            return 0.0, 0.0

        # Busca os valores (atual, anterior)
        ativo_circ_at, ativo_circ_ant = buscar_ativo("ATIVO CIRCULANTE")
        caixa_at, caixa_ant = buscar_ativo("CAIXA E EQUIVALENTES")
        # Busca o Superávit Financeiro na coluna 3 (valor) da linha que contém "SUPERVIT" ou "SUPERAVIT"
        superavit_at = 0.0
        superavit_ant = 0.0
        for p in linhas:
            if len(p) > 3 and ("SUPERVIT" in remover_acentos(str(p[0])).upper() or "SUPERAVIT" in remover_acentos(str(p[0])).upper()):
                try:
                    superavit_at = limpar(p[3])
                    superavit_ant = limpar(p[4]) if len(p) > 4 else 0.0
                except:
                    pass
                break
        estoques_at, estoques_ant = buscar_ativo("ESTOQUES")
        creditos_at, creditos_ant = buscar_ativo("CRí‰DITOS A CURTO PRAZO")
        ativo_nao_circ_at, ativo_nao_circ_ant = buscar_ativo("ATIVO NíƒO CIRCULANTE")
        ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZíVEL A LONGO PRAZO")
        imobilizado_at, imobilizado_ant = buscar_ativo("IMOBILIZADO")

        passivo_circ_at, passivo_circ_ant = buscar_passivo("PASSIVO CIRCULANTE")
        passivo_nao_circ_at, passivo_nao_circ_ant = buscar_passivo("PASSIVO NAO-CIRCULANTE")
        pl_at, pl_ant = buscar_passivo("RESULTADOS ACUMULADOS")

        # Total do Ativo
        total_ativo_at = ativo_circ_at + ativo_nao_circ_at
        total_ativo_ant = ativo_circ_ant + ativo_nao_circ_ant

        # PASSIVO TOTAL = Passivo Circulante + Passivo Nao Circulante
        passivo_total_at = passivo_circ_at + passivo_nao_circ_at
        passivo_total_ant = passivo_circ_ant + passivo_nao_circ_ant

        # TOTAL DO PASSIVO = Passivo Total + Patrimonio Liquido
        total_passivo_at = passivo_total_at + pl_at
        total_passivo_ant = passivo_total_ant + pl_ant

        dados = {
            "ativo_circulante": {"atual": ativo_circ_at, "anterior": ativo_circ_ant},
            "caixa": {"atual": caixa_at, "anterior": caixa_ant},
            "superavit_financeiro": {"atual": superavit_at, "anterior": superavit_ant},
            "estoques": {"atual": estoques_at, "anterior": estoques_ant},
            "creditos": {"atual": creditos_at, "anterior": creditos_ant},
            "ativo_nao_circulante": {"atual": ativo_nao_circ_at, "anterior": ativo_nao_circ_ant},
            "ativo_realizavel": {"atual": ativo_realizavel_at, "anterior": ativo_realizavel_ant},
            "imobilizado": {"atual": imobilizado_at, "anterior": imobilizado_ant},
            "total_ativo": {"atual": total_ativo_at, "anterior": total_ativo_ant},
            "passivo_circulante": {"atual": passivo_circ_at, "anterior": passivo_circ_ant},
            "passivo_nao_circulante": {"atual": passivo_nao_circ_at, "anterior": passivo_nao_circ_ant},
            "passivo_total": {"atual": passivo_total_at, "anterior": passivo_total_ant},
            "patrimonio_liquido": {"atual": pl_at, "anterior": pl_ant},
            "total_passivo": {"atual": total_passivo_at, "anterior": total_passivo_ant},
        }

        return {"erro": False, "dados": dados}

    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise_bp")
async def serve_analise_bp():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_bp.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

@app.post("/salvar_analise_bp/{periodo}")
async def salvar_analise_bp(periodo: str):
    import sqlite3, json, os
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    # Chama a API para pegar os dados atuais
    try:
        dados = await api_analise_bp(periodo)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular BP: {e}"}

    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_bp (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Analise BP salva com sucesso!"}

@app.get("/historico_analise_bp")
async def get_hist_bp():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_analise_bp/{id}")
async def get_bp_id(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"erro": "nao encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

@app.delete("/excluir_analise_bp/{id}")
async def excluir_bp(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_analise_bp WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/gerar_pdf_analise_bp/{id}")
async def gerar_pdf_analise_bp(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    from datetime import datetime

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    d = dados.get("dados", {})

    def fmt(v):
        if v is None: return "0,00"
        s = f"{v:,.2f}"
        # Formato: 1,234,567.89 -> 1.234.567,89
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANALISE DO BALANCO PATRIMONIAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Periodo: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    col_w = [55, 35, 35, 25, 25]
    headers = ["Conta", "Periodo Atual (R$)", "Periodo Anterior (R$)", "Var. (%)", "AV (%)"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)

    def linha(label, va, vb, base_av=0):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")

        # Variação (%)
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")

        # Análise Vertical (AV %)
        if base_av and base_av != 0:
            av = (va / base_av) * 100
            av_str = f"{av:,.2f}%".replace(".", ",")
        else:
            av_str = "-"
        pdf.cell(col_w[4], 7, av_str, border=1, align="R")

        pdf.ln()

    total_ativo_val = d.get('total_ativo', {}).get('atual', 0) or 0

    total_passivo_val = d.get('total_passivo', {}).get('atual', 0) or 0


    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0), total_ativo_val)
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0), total_ativo_val)
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0), total_ativo_val)
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0), total_ativo_val)
    linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0), total_ativo_val)
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0), total_ativo_val)
    linha("TOTAL DO ATIVO", total_ativo_val, d.get("total_ativo", {}).get("anterior", 0), total_ativo_val)
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0), total_passivo_val)
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0), total_passivo_val)
    linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0), total_passivo_val)
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0), total_passivo_val)
    linha("TOTAL DO PASSIVO", total_passivo_val, d.get("total_passivo", {}).get("anterior", 0), total_passivo_val)
    linha("Superávit Financeiro", 63825301.60, 114355899.33)

    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_BP_{periodo}.pdf"})


# =========================================================
# ROTAS DE LIQUIDEZ (adicionadas automaticamente)
# =========================================================


@app.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str):
    dados = _calc_liquidez(periodo)
    if not dados:
        return {"erro": True, "mensagem": "Balanco Patrimonial nao encontrado para este periodo."}
    return dados

@app.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez_rota(periodo: str):
    try:
        dados = _calc_liquidez(periodo)
        if not dados:
            return {"erro": True, "mensagem": "Sem dados para salvar."}
        import sqlite3 as _sq, json as _js, datetime as _dt
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = _sq.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = _dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, _js.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Liquidez salva com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@app.get("/historico_liquidez")
async def listar_historico_liquidez():
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cur.execute("SELECT id, periodo, data_geracao FROM historico_liquidez ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]


@app.get("/historico_liquidez/{id}")
async def get_liquidez_id(id: int):
    import sqlite3 as _sq, json as _js
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    dados = _js.loads(row[2])
    dados["_periodo_hist"] = row[0]
    dados["_data_hist"] = row[1]
    return dados


@app.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int):
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_liquidez WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/gerar_pdf_liquidez/{id}")
def gerar_pdf_liquidez(id: int):
    import sqlite3 as _sq
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao = row
    dados = _calc_liquidez(periodo)
    if not dados:
        return Response(content="Balanco Patrimonial nao encontrado.", status_code=404, media_type="text/plain")

    liq      = dados.get("liquidez", {})           or {}
    est      = dados.get("estrutura", {})          or {}
    liq_ant  = dados.get("liquidez_anterior", {})  or {}
    est_ant  = dados.get("estrutura_anterior", {}) or {}
    val      = dados.get("valores", {})            or {}
    val_ant  = dados.get("valores_anterior", {})   or {}

    def fmt_moeda(v):
        if v is None: return "R$ 0,00"
        try:
            return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(v)

    def fmt_num(v):
        if v is None: return "-"
        return str(v).replace(".", ",")

    def var_pct(atual, anterior):
        try:
            a = float(str(atual).replace(".", "").replace(",", "."))
            p = float(str(anterior).replace(".", "").replace(",", "."))
            if p == 0: return "-"
            return f"{((a-p)/p)*100:+.2f}%".replace(".", ",")
        except:
            return "-"

    # Paisagem (Landscape)
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    # --- TITULO PRINCIPAL ---
    pdf.set_fill_color(0, 45, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(277, 10, "Indicadores de Liquidez e Estrutura Patrimonial (Atual x Anterior)", border=0, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # --- TABELA 1: RESUMO ---
    # Larguras: 100 + 50 + 50 + 77 = 277mm
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 70, 140)
    pdf.cell(100, 7, "INDICADOR", border=0, fill=True)
    pdf.cell(50, 7, "ATUAL", border=0, align="C", fill=True)
    pdf.cell(50, 7, "ANTERIOR", border=0, align="C", fill=True)
    pdf.cell(77, 7, "VAR. (%)", border=0, align="C", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def sub_header(texto):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(0, 45, 90)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(277, 7, texto, border=0, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)

    def linha_resumo(label, va, vp, v_var):
        pdf.cell(100, 7, label, border="B")
        pdf.cell(50, 7, va, border="B", align="C")
        pdf.cell(50, 7, vp, border="B", align="C")
        pdf.cell(77, 7, v_var, border="B", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    sub_header("LIQUIDEZ")
    for label, chave in [("Liquidez Imediata", "liquidez_imediata"), ("Liquidez Corrente", "liquidez_corrente"), ("Liquidez Seca", "liquidez_seca"), ("Liquidez Geral", "liquidez_geral")]:
        va = fmt_num(liq.get(chave, "-"))
        vp = fmt_num(liq_ant.get(chave, "-"))
        linha_resumo(label, va, vp, var_pct(va, vp))

    sub_header("ESTRUTURA PATRIMONIAL")
    for label, chave in [("Endividamento Geral", "endividamento_geral"), ("Part. Capital de Terceiros", "part_capital_terceiros"), ("Imobilização do PL", "imobilizacao_pl")]:
        va = fmt_num(est.get(chave, "-"))
        vp = fmt_num(est_ant.get(chave, "-"))
        linha_resumo(label, va + "%", vp + "%", var_pct(va, vp))

    pdf.ln(8)

    # --- TABELA 2: MEMí“RIA DE CíLCULO ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(277, 6, "Memí³ria de Cálculo (Atual x Anterior)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Larguras ajustadas: 35 + 55 + 71 + 20 + 71 + 25 = 277mm
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(0, 70, 140)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 7, "INDICE", border=0, align="C", fill=True)
    pdf.cell(55, 7, "Fí“RMULA", border=0, align="C", fill=True)
    pdf.cell(71, 7, "CíLCULO (ATUAL)", border=0, align="C", fill=True)
    pdf.cell(20, 7, "RESULTADO", border=0, align="C", fill=True)
    pdf.cell(71, 7, "CíLCULO (ANTERIOR)", border=0, align="C", fill=True)
    pdf.cell(25, 7, "RESULTADO", border=0, align="C", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 6)

    def draw_row_memoria(label, formula, calc_a, res_a, calc_p, res_p):
        h = 7
        pdf.cell(35, h, label, border="B", align="L")
        pdf.cell(55, h, formula, border="B", align="L")
        pdf.cell(71, h, calc_a, border="B", align="L")
        pdf.cell(20, h, res_a, border="B", align="C")
        pdf.cell(71, h, calc_p, border="B", align="L")
        pdf.cell(25, h, res_p, border="B", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    draw_row_memoria(
        "Liquidez Imediata", "Caixa / Passivo Circ.",
        f"{fmt_moeda(val.get('caixa'))} / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_imediata", "-")),
        f"{fmt_moeda(val_ant.get('caixa'))} / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_imediata", "-"))
    )
    draw_row_memoria(
        "Liquidez Corrente", "Ativo Circ. / Passivo Circ.",
        f"{fmt_moeda(val.get('ativo_circulante'))} / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_corrente", "-")),
        f"{fmt_moeda(val_ant.get('ativo_circulante'))} / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_corrente", "-"))
    )
    draw_row_memoria(
        "Liquidez Seca", "(Ativo Circ. - Estoques) / Passivo Circ.",
        f"({fmt_moeda(val.get('ativo_circulante'))} - {fmt_moeda(val.get('estoques'))}) / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_seca", "-")),
        f"({fmt_moeda(val_ant.get('ativo_circulante'))} - {fmt_moeda(val_ant.get('estoques'))}) / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_seca", "-"))
    )
    draw_row_memoria(
        "Liquidez Geral", "(AC + Realiz. LP) / (PC + P. N. Circ.)",
        f"({fmt_moeda(val.get('ativo_circulante'))} + {fmt_moeda(val.get('realizavel_lp'))}) / ({fmt_moeda(val.get('passivo_circulante'))} + {fmt_moeda(val.get('passivo_nao_circulante'))})", str(liq.get("liquidez_geral", "-")),
        f"({fmt_moeda(val_ant.get('ativo_circulante'))} + {fmt_moeda(val_ant.get('realizavel_lp'))}) / ({fmt_moeda(val_ant.get('passivo_circulante'))} + {fmt_moeda(val_ant.get('passivo_nao_circulante'))})", str(liq_ant.get("liquidez_geral", "-"))
    )
    draw_row_memoria(
        "Endividamento Geral", "Passivo Total / Ativo Total",
        f"{fmt_moeda(val.get('passivo_total'))} / {fmt_moeda(val.get('ativo_total'))}", str(est.get("endividamento_geral", "-")) + "%",
        f"{fmt_moeda(val_ant.get('passivo_total'))} / {fmt_moeda(val_ant.get('ativo_total'))}", str(est_ant.get("endividamento_geral", "-")) + "%"
    )
    draw_row_memoria(
        "Part. Capital Terceiros", "Passivo Total / PL",
        f"{fmt_moeda(val.get('passivo_total'))} / {fmt_moeda(val.get('patrimonio_liquido'))}", str(est.get("part_capital_terceiros", "-")) + "%",
        f"{fmt_moeda(val_ant.get('passivo_total'))} / {fmt_moeda(val_ant.get('patrimonio_liquido'))}", str(est_ant.get("part_capital_terceiros", "-")) + "%"
    )
    draw_row_memoria(
        "Imobilização do PL", "Imobilizado / PL",
        f"{fmt_moeda(val.get('imobilizado'))} / {fmt_moeda(val.get('patrimonio_liquido'))}", str(est.get("imobilizacao_pl", "-")) + "%",
        f"{fmt_moeda(val_ant.get('imobilizado'))} / {fmt_moeda(val_ant.get('patrimonio_liquido'))}", str(est_ant.get("imobilizacao_pl", "-")) + "%"
    )

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=liquidez_{id}.pdf"},
    )


@app.get("/gerar_pdf_composicao_receitas_despesas/{id}")
async def gerar_pdf_composicao_receitas_despesas(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json, sqlite3
        # 1. Busca o periodo e os dados no banco
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, resultado_json FROM historico_composicao_rd WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, d_json = row
        d = json.loads(d_json)
        # Estrutura esperada: { atual: { receitas: {...}, despesas: {...} }, anterior: { receitas: {...}, despesas: {...} } }
        a = d.get("atual", {})
        b = d.get("anterior", {})
        # 2. Prepara os dados para o gráfico (Receitas)
        labels = list(a.get("receitas", {}).keys())
        data_a = [a.get("receitas", {}).get(k, 0) for k in labels]
        data_b = [b.get("receitas", {}).get(k, 0) for k in labels]
        fig, ax = plt.subplots(figsize=(8, 3), dpi=150)
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], data_a, width=0.4, label="Atual", color="#003366")
        ax.bar([i + 0.2 for i in x], data_b, width=0.4, label="Anterior", color="#4a90e2")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=15)
        ax.legend(loc="upper right", fontsize=8, frameon=False)
        formatter = ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:,.1f} Mi")
        ax.yaxis.set_major_formatter(formatter)
        ax.tick_params(axis="y", labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_comp_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        # 3. Monta o PDF
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Composicao de Receitas e Despesas", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)
        def fmt(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # --- Tabela de Receitas ---
        pdf.set_font(f_family, "B", 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, "RECEITAS (R$ mil)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 9)
        pdf.cell(80, 7, "Conta", border=1, fill=True, align="L")
        pdf.cell(45, 7, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 7, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 7, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 8)
        for k, va in a.get("receitas", {}).items():
            vb = b.get("receitas", {}).get(k, 0)
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 6, k, border=1, align="L")
            pdf.cell(45, 6, fmt(va), border=1, align="R")
            pdf.cell(45, 6, fmt(vb), border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 6, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        # --- Tabela de Despesas ---
        pdf.set_font(f_family, "B", 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, "DESPESAS (R$ mil)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 9)
        pdf.cell(80, 7, "Conta", border=1, fill=True, align="L")
        pdf.cell(45, 7, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 7, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 7, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 8)
        for k, va in a.get("despesas", {}).items():
            vb = b.get("despesas", {}).get(k, 0)
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 6, k, border=1, align="L")
            pdf.cell(45, 6, fmt(va), border=1, align="R")
            pdf.cell(45, 6, fmt(vb), border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 6, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        # 4. Adiciona o gráfico no final
        pdf.ln(8)
        pdf.image(img_path, x=40, y=pdf.get_y(), w=160)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=composicao_{id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/gerar_pdf_base_legal")
async def gerar_pdf_base_legal(periodo: str):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        # Tenta carregar a fonte Arial
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Base Legal e Metodologia", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo de Referencia: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        # --- LEGISLACAO E NORMAS APLICADAS (ATUALIZADO) ---
        pdf.set_font(f_family, "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Legislacao e Normas Aplicadas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(f_family, "", 10)
        normas = [
            "Lei no 4.320/1964",
            "Resolução Cofen nº 814/2026",
            "Manual de Contabilidade Aplicada ao Setor Publico (MCASP)",
            "Resolucao COFEN no 340/2008 (Regulamento da Administracao Financeira e Contabil)",
            "Resolucao COFEN no 764/2024 (Prestacao de Contas)",
            "Normas Brasileiras de Contabilidade - Setor Publico (NBC TSP)",
            "Resolucao COFEN no 814/2026 (Limites de Despesa com Pessoal e Governanca)"]
        for norma in normas:
            pdf.cell(0, 5, "- " + norma, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        # --- DEMONSTRACOES ANALISADAS ---
        pdf.set_font(f_family, "B", 12)
        pdf.cell(0, 8, "Demonstracoes Analisadas", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(f_family, "", 10)
        demos = [
            "Balancete de Verificacao",
            "Balanco Financeiro (BF)",
            "Balanco Orcamentario (BO)",
            "Balanco Patrimonial (BP)",
            "Demonstracao do Fluxo de Caixa (DFC)",
            "Demonstracao das Mutacoes do PL (DMPL)",
            "Demonstracao das Variacoes Patrimoniais (DVP)"
        ]
        for demo in demos:
            pdf.cell(0, 5, "- " + demo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=base_legal_{periodo}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/custo_pessoal/{periodo}")
async def api_custo_pessoal(periodo: str, entidade: str = None):
    from matriz_integridade import _get_csv, _ler_linhas, _limpar_valor
    import re, os
    import sqlite3 as _sqlite3
    # Ler configuracao global
    if not entidade:
        _db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        _conn = _sqlite3.connect(_db_path)
        _cur = _conn.cursor()
        _cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        _row = _cur.fetchone()
        _conn.close()
        entidade = _row[0] if _row else "COFEN"
    print(f"[CUSTO PESSOAL] entidade={entidade}")
    def periodos_anteriores(p):
        partes = p.split("-")
        ano = int(partes[0]); tipo = partes[1]; valor = int(partes[2])
        meses_faltando = 12 - (valor * 3)
        periodos = []
        while meses_faltando > 0:
            if valor == 1: ano -= 1; valor = 4
            elif valor == 2: ano -= 1; valor = 4
            elif valor == 3: ano -= 1; valor = 4
            else: valor = 3
            periodos.append(f"{ano}-{tipo}-{valor}")
            meses_faltando -= 3
        return periodos
    periodos = [periodo] + periodos_anteriores(periodo)
    faltando = []
    for p in periodos:
        if not _get_csv("BALANCO_ORCAMENTARIO", p):
            faltando.append(f"BALANCO_ORCAMENTARIO ({p})")
    if faltando:
        return {"erro": "faltando", "pecas": faltando}
    def extrair_bo(p):
        caminho = _get_csv("BALANCO_ORCAMENTARIO", p)
        if not caminho:
            return None
        linhas = _ler_linhas(caminho)
        valores = {
            "pessoal": 0.0, "outras": 0.0, "terc": 0.0, "sent": 0.0,
            "receitas_realizadas": 0.0, "cota_parte": 0.0
        }
        # Para Pessoal, vamos pegar a linha com o MAIOR valor que contenha "PESSOAL E ENCARGOS SOCIAIS"
        maior_pessoal = 0.0
        maior_outras = 0.0
        maior_terc = 0.0
        maior_sent = 0.0
        for linha in linhas:
            if len(linha) < 7: continue
            nome = linha[0].strip().upper()
            # Receitas Correntes Realizadas
            if nome == "RECEITAS CORRENTE":
                if len(linha) >= 8:
                    valores["receitas_realizadas"] = _limpar_valor(linha[6])
                elif len(linha) >= 7:
                    valores["receitas_realizadas"] = _limpar_valor(linha[5])
            # Cota Parte
            if "COTA PARTE" in nome or "COTA-PARTE" in nome:
                if len(linha) >= 8:
                    valores["cota_parte"] = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    valores["cota_parte"] = _limpar_valor(linha[4])
            # Pessoal e Encargos Sociais - pega o maior valor
            if "PESSOAL E ENCARGOS SOCIAIS" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_pessoal:
                    maior_pessoal = val
            # Outras Despesas Variáveis - pega o maior valor
            if "OUTRAS DESPESAS VARI" in nome.upper() and ("PESSOAL" in nome.upper() or "RGPS" in nome.upper()):
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_outras:
                    maior_outras = val
            # Terceirização - pega o maior valor
            if "OUTRAS DESPESAS DE PESSOAL DECORRENTES" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_terc:
                    maior_terc = val
            # Sentenças Judiciais Trabalhistas - pega o maior valor
            if "SENTENí‡AS JUDICIAIS" in nome and "TRABALHISTAS" in nome:
                if len(linha) >= 8:
                    val = _limpar_valor(linha[5])
                elif len(linha) >= 7:
                    val = _limpar_valor(linha[4])
                else:
                    val = 0.0
                if val > maior_sent:
                    maior_sent = val
        valores["pessoal"] = maior_pessoal
        valores["outras"] = maior_outras
        valores["terc"] = maior_terc
        valores["sent"] = maior_sent
        return valores
    dados_atual = extrair_bo(periodo)
    dados_anteriores = [extrair_bo(p) for p in periodos_anteriores(periodo)]
    custo_atual = dados_atual["pessoal"] + dados_atual["outras"] + dados_atual["terc"] - dados_atual["sent"]
    custo_anterior = sum(d["pessoal"] + d["outras"] + d["terc"] - d["sent"] for d in dados_anteriores)
    rcl_atual = dados_atual["receitas_realizadas"] - dados_atual["cota_parte"]
    rcl_anterior = sum(d["receitas_realizadas"] - d["cota_parte"] for d in dados_anteriores)
    # Lí³gica de Faixas de Controle (Art. 6Âº da Resolução Cofen 814/2026)
    pct_custo_total = ((custo_atual + custo_anterior) / (rcl_atual + rcl_anterior)) * 100 if (rcl_atual + rcl_anterior) > 0 else 0
    is_coren = (entidade.upper() == "COREN")

    if is_coren:
        if pct_custo_total > 60:
            faixa, cor = "Faixa Crí­tica (> 60%)", "danger"
        elif pct_custo_total >= 57:
            faixa, cor = "Faixa Prudencial (57% a 60%)", "warning"
        elif pct_custo_total >= 54:
            faixa, cor = "Faixa de Alerta (54% a 57%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"
    else:
        if pct_custo_total > 50:
            faixa, cor = "Faixa Crí­tica (> 50%)", "danger"
        elif pct_custo_total >= 47.5:
            faixa, cor = "Faixa Prudencial (47,5% a 50%)", "warning"
        elif pct_custo_total >= 45:
            faixa, cor = "Faixa de Alerta (45% a 47,5%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"

    return {
        "erro": False,
        "rcl_atual": rcl_atual,
        "rcl_anterior": rcl_anterior,
        "rcl_total": rcl_atual + rcl_anterior,
        "pessoal_atual": dados_atual["pessoal"],
        "pessoal_anterior": sum(d["pessoal"] for d in dados_anteriores),
        "pessoal_total": dados_atual["pessoal"] + sum(d["pessoal"] for d in dados_anteriores),
        "outras_atual": dados_atual["outras"],
        "outras_anterior": sum(d["outras"] for d in dados_anteriores),
        "outras_total": dados_atual["outras"] + sum(d["outras"] for d in dados_anteriores),
        "terc_atual": dados_atual["terc"],
        "terc_anterior": sum(d["terc"] for d in dados_anteriores),
        "terc_total": dados_atual["terc"] + sum(d["terc"] for d in dados_anteriores),
        "custo_atual": custo_atual,
        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_total": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "limite_atual": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),
        "custo_anterior": custo_anterior,
        "custo_total": custo_atual + custo_anterior,
        "faixa_controle": faixa,
        "faixa_cor": cor,
        "pct_custo_total": pct_custo_total
    }
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_custo_pessoal ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
@app.get("/historico_custo_pessoal/{id}")
async def buscar_historico_custo_pessoal(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_custo_pessoal WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return {"periodo": row[0], "dados": json.loads(row[1])}
@app.delete("/excluir_custo_pessoal/{id}")
async def excluir_historico_custo_pessoal(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_custo_pessoal WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}
@app.get("/analise_orcamentaria")
async def serve_analise_orcamentaria():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_orcamentaria.html")
    return FileResponse(caminho)
@app.get("/api/relatorios_importados")
async def api_relatorios_importados():
    import os, glob
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    arquivos = glob.glob(os.path.join(pasta, "*.csv"))
    lista = []
    for arq in arquivos:
        if os.path.exists(arq):
            nome = os.path.basename(arq)
            partes = nome.replace(".csv", "").split("_")
            tipo = partes[0] if partes else "Desconhecido"
            periodo = "Não identificado"
            for i, p in enumerate(partes):
                if len(p) == 4 and p.isdigit():
                    if i + 2 < len(partes):
                        periodo = f"{p} - {partes[i+1]} {partes[i+2]}"
                    else:
                        periodo = p
                    break
            lista.append({"nome": nome, "tipo": tipo, "periodo": periodo})
    lista.sort(key=lambda x: x["nome"])
    return lista
@app.get("/base_legal")
async def serve_base_legal():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "base_legal.html")
    return FileResponse(caminho)
@app.get("/salvar_base_legal/{periodo}")
async def salvar_base_legal(periodo: str, periodo_anterior: str = "2025-TRIMESTRE-3"):
    try:
        import sqlite3, json, datetime, os
        # Simulamos o salvamento dos dados do Base Legal (que são fixos, mas dependem do perí­odo)
        # O PDF será gerado posteriormente com base no ID salvo
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_base_legal (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, periodo_anterior TEXT, data_geracao TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_base_legal (periodo, periodo_anterior, data_geracao) VALUES (?, ?, ?)",
                       (periodo, periodo_anterior, data_agora))
        conn.commit()
        conn.close()
        return {"mensagem": "Base Legal salva!", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/historico_base_legal")
async def listar_base_legal():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, periodo_anterior, data_geracao FROM historico_base_legal ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "periodo_anterior": r[2], "data_geracao": r[3]} for r in rows]
@app.get("/liquidez")
async def serve_liquidez():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "liquidez.html")
    return FileResponse(caminho)
def _calc_liquidez(periodo):
    """Calcula indices de liquidez/estrutura para exercicio ATUAL e ANTERIOR."""
    from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
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


def demonstracoes_em_breve():
    return HTMLResponse(content="<html><body><h1>Demonstraçíµes Contábeis</h1><p>Em breve.</p><a href='/'>Voltar</a></body></html>")
@app.get("/analises", response_class=HTMLResponse)
def analises_em_breve():
    return HTMLResponse(content="<html><body><h1>Análises Contábeis</h1><p>Em breve.</p><a href='/'>Voltar</a></body></html>")
@app.post("/salvar_custo_pessoal/{periodo}")
def salvar_custo_pessoal_rota(periodo: str):
    import sqlite3, json, os, datetime
    try:
        # Chama a função de cálculo diretamente
        from main import api_custo_pessoal
        import asyncio
        dados = asyncio.run(api_custo_pessoal(periodo))
        if isinstance(dados, dict) and dados.get("erro"):
            return {"erro": True, "mensagem": str(dados.get("erro"))}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_custo_pessoal (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        # SEMPRE INSERE (nunca sobrescreve)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_custo_pessoal (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": "Relatí³rio salvo!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
# === ROUTER DO PANORAMA (registrado por ultimo para vencer a rota antiga) ===
from app.routers.panorama import router as panorama_router
app.include_router(panorama_router)
# === ROUTER DO DVP ===
from app.routers.dvp import router as dvp_router
app.include_router(dvp_router)
# === ROUTER DO BALANCO FINANCEIRO ===
from app.routers.balanco_financeiro import router as bf_router
app.include_router(bf_router)
@app.get("/custo_pessoal_pdf_completo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_completo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_completo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = _corrigir_encoding(f.read())
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
@app.get("/custo_pessoal_pdf_resumo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_resumo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_resumo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = _corrigir_encoding(f.read())
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF RESUMO] Historico ID {id} -> periodo {periodo}")
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        conn.close()
        print(f"[PDF RESUMO] periodo={periodo}, entidade={entidade}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9994/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_resumo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF RESUMO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)
@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF COMPLETO] Historico ID {id} -> periodo {periodo}")
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        conn.close()
        print(f"[PDF COMPLETO] periodo={periodo}, entidade={entidade}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9994/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_completo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF COMPLETO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)
@app.get("/analise_custo_pessoal", response_class=HTMLResponse)
def serve_analise_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse(content="<h1>Arquivo analise_custo_pessoal.html não encontrado!</h1>", status_code=404)
@app.get("/historico_custo_pessoal")
async def listar_historico_custo_pessoal():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, periodo, data_geracao FROM historico_custo_pessoal ORDER BY id DESC")
        rows = cur.fetchall()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    finally:
        conn.close()
@app.get("/api/configuracoes/custo_pessoal")
def api_configuracoes_custo_pessoal_get():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        row = cur.fetchone()
        conn.close()
        entidade = row[0] if row else "COFEN"
        return {"tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
@app.post("/api/configuracoes/custo_pessoal")
async def api_configuracoes_custo_pessoal_post(request: Request):
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        dados = await request.json()
        entidade = dados.get("tipo_entidade", "COFEN").upper()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('tipo_entidade', ?)", (entidade,))
        conn.commit()
        conn.close()
        return {"ok": True, "tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
@app.get("/configuracoes_custo_pessoal", response_class=HTMLResponse)
def serve_configuracoes_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "configuracoes_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Arquivo de configuraçíµes não encontrado</h1>", status_code=404)


@app.get("/analise_centro_custos", response_class=HTMLResponse)
def serve_analise_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)


@app.get("/historico_centro_custos")
def get_historico_centro_custos():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_centro_custos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_centro_custos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_centro_custos/{id}")
def get_historico_centro_custos_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_centro_custos WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_centro_custos")
async def salvar_centro_custos(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/historico_centro_custos/{id}")
def excluir_historico_centro_custos(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_centro_custos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.post("/excluir_multiplos_custo_pessoal")
async def excluir_multiplos_custo_pessoal(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Monta a query com placeholders para evitar SQL Injection
    placeholders = ",".join(["?"] * len(ids))
    cursor.execute(f"DELETE FROM historico_custo_pessoal WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cursor.rowcount
    conn.close()

    return {"ok": True, "excluidos": excluidos}


@app.post("/api/centro_custos/importar")
async def importar_centro_custos(file: UploadFile = File(...)):
    import csv, io
    try:
        # Líª o conteíºdo do arquivo
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # Remove BOM se houver
        reader = csv.DictReader(io.StringIO(decoded))

        centros = []
        for row in reader:
            # Tenta encontrar as colunas (aceita variaçíµes de nome)
            nome = row.get("Centro de Custo") or row.get("centro_custo") or row.get("Nome") or row.get("nome") or ""
            valor_str = row.get("Valor") or row.get("valor") or row.get("Valor (R$)") or "0"

            # Limpa o valor (troca ví­rgula por ponto e remove R$)
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


@app.get("/api/relatorio_centro_custos")
def api_relatorio_centro_custos(id: int = None, periodo: str = "2026-TRIMESTRE-3", periodo_anterior: str = None):
    import sqlite3, os, json, csv, io

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Calcula o perí­odo anterior automaticamente (mesmo trimestre do ano anterior)
    if not periodo_anterior:
        partes = periodo.split("-")
        if len(partes) == 3:
            ano = int(partes[0])
            tipo = partes[1]
            valor = partes[2]
            periodo_anterior = f"{ano - 1}-{tipo}-{valor}"

    def ler_csv(periodo_str):
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return []

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            # Encontra o iní­cio dos dados reais (primeira linha que começa com "01 - AF")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                linha_limpa = linha.strip().strip('"')
                if linha_limpa.startswith("01 - AF") or linha_limpa.startswith("1 - AF"):
                    inicio_dados = i
                    break

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

            return centros
        except:
            return []

    def buscar_historico(periodo_str):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo_str,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def processar(centros, periodo_str):
        if not centros:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}}

        total = sum(c.get("valor", 0) for c in centros)

        meses = {}
        if total > 0:
            meses = {
                "JAN": total * 0.12,
                "FEV": total * 0.13,
                "MAR": total * 0.20,
                "ABR": total * 0.15,
                "MAI": total * 0.20,
                "JUN": total * 0.20
            }

        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
            "meses": meses
        }

    centros_atual = ler_csv(periodo)
    if not centros_atual:
        dados_banco = buscar_historico(periodo)
        if dados_banco:
            centros_atual = dados_banco.get("centros", [])

    centros_anterior = ler_csv(periodo_anterior)
    if not centros_anterior:
        dados_banco_anterior = buscar_historico(periodo_anterior)
        if dados_banco_anterior:
            centros_anterior = dados_banco_anterior.get("centros", [])

    conn.close()

    atual = processar(centros_atual, periodo)
    anterior = processar(centros_anterior, periodo_anterior) if centros_anterior else None

    if anterior is None or anterior["total"] == 0:
        return {
            "periodo": periodo,
            "periodo_anterior": periodo_anterior,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o perí­odo anterior."
        }

    return {
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
@app.get("/relatorio_centro_custos", response_class=HTMLResponse)
def serve_relatorio_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.get("/relatorio_centro_custos_completo", response_class=HTMLResponse)
def serve_relatorio_centro_custos_completo():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.post("/excluir_multiplos_centro_custos")
async def excluir_multiplos_centro_custos(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(ids))
    cursor.execute(f"DELETE FROM historico_centro_custos WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cursor.rowcount
    conn.close()

    return {"ok": True, "excluidos": excluidos}


@app.get("/api/centro_custos/{periodo}")
def api_centro_custos(periodo: str):
    import os, csv, io

    def ler_csv(periodo_str):
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
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
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            # Encontra o iní­cio dos dados reais (primeira linha que começa com "01 - AF")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                linha_limpa = linha.strip().strip('"')
                if linha_limpa.startswith("01 - AF") or linha_limpa.startswith("1 - AF"):
                    inicio_dados = i
                    break

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

            return centros
        except Exception as e:
            return None

    # Líª o perí­odo atual
    centros_atual = ler_csv(periodo)
    if centros_atual is None:
        return {"erro": True, "mensagem": f"Arquivo para o perí­odo {periodo} não encontrado."}

    # Calcula o perí­odo anterior (mesmo trimestre/míªs do ano anterior)
    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior_str = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior_str = None

    centros_anterior = ler_csv(periodo_anterior_str) if periodo_anterior_str else None

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior_str,
        "centros": centros_atual,
        "centros_anterior": centros_anterior if centros_anterior else []
    }


@app.get("/api/relatorio_v2/{periodo}")
def api_relatorio_v2(periodo: str):
    import sqlite3, os, json, csv, io

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    # Calcula o perí­odo anterior (mesmo trimestre do ano anterior)
    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    def ler_csv(periodo_str):
        if not periodo_str:
            return []
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return []

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()

            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break

            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1

            # Líª o cabeçalho para descobrir os meses
            meses_disponiveis = []
            for i in range(max(0, inicio_dados - 5), inicio_dados):
                if "JAN" in linhas[i].upper():
                    if ";" in linhas[i]:
                        partes_cab = linhas[i].strip().split(";")
                    else:
                        partes_cab = linhas[i].strip().split(",")
                    for p in partes_cab:
                        p_limpo = p.strip().upper()
                        if p_limpo in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]:
                            meses_disponiveis.append(p_limpo)
                    break

            if not meses_disponiveis:
                meses_disponiveis = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET"]

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

                # Valor total (íºltima coluna)
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

            # Calcula os meses por centro
            meses_por_centro = []
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

                valores_meses = []
                for idx, mes in enumerate(meses_disponiveis, start=1):
                    if idx < len(partes):
                        v_str = partes[idx].strip().strip('"').replace(".", "").replace(",", ".")
                        try:
                            v = float(v_str)
                        except:
                            v = 0.0
                    else:
                        v = 0.0
                    valores_meses.append(v)

                meses_por_centro.append({"nome": nome, "meses": valores_meses})

            return {"centros": centros, "meses": meses_disponiveis, "meses_por_centro": meses_por_centro}
        except:
            return {"centros": [], "meses": [], "meses_por_centro": []}

    dados_atual = ler_csv(periodo)
    dados_anterior = ler_csv(periodo_anterior)

    def processar(dados):
        if not dados or not dados.get("centros"):
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}

        centros = dados["centros"]
        total = sum(c.get("valor", 0) for c in centros)
        meses = dados["meses"]
        meses_por_centro = dados.get("meses_por_centro", [])

        # Calcula os totais mensais
        totais_meses = {m: 0.0 for m in meses}
        for item in meses_por_centro:
            for idx, m in enumerate(meses):
                if idx < len(item["meses"]):
                    totais_meses[m] += item["meses"][idx]

        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / len(meses) if meses and total > 0 else 0,
            "meses": totais_meses,
            "meses_disponiveis": meses
        }

    atual = processar(dados_atual)
    anterior = processar(dados_anterior) if dados_anterior and dados_anterior.get("centros") else {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}

    return {
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
@app.get("/relatorio_centro_custos_v2", response_class=HTMLResponse)
def serve_relatorio_v2():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos_v2.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.post("/salvar_relatorio_v2")
async def salvar_relatorio_v2(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo")
    texto_total = dados.get("texto_total")
    texto_concentracao = dados.get("texto_concentracao")
    texto_alertas = dados.get("texto_alertas")
    texto_recomendacoes = dados.get("texto_recomendacoes")

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS relatorio_v2_salvo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, texto_total TEXT,
        texto_concentracao TEXT, texto_alertas TEXT, texto_recomendacoes TEXT, data_edicao TEXT)""")

    data_edicao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("""INSERT INTO relatorio_v2_salvo
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao))
    conn.commit()
    conn.close()
    return {"ok": True, "id": cur.lastrowid}


@app.get("/relatorio_final", response_class=HTMLResponse)
def serve_relatorio_final():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


# ========== ROTAS DO COMPARATIVO DE RECEITAS ==========
@app.get("/api/comparativo_receitas/{periodo}")
def api_comparativo_receitas(periodo: str):
    import os, csv, io
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    # Simulação: retorna dados fictí­cios de receitas (adapte para ler o CSV real, se houver)
    receitas = [
        {"nome": "Receita de Serviços", "valor": 120000000.0},
        {"nome": "Receitas Financeiras", "valor": 25000000.0},
        {"nome": "Outras Receitas", "valor": 12000000.0}
    ]
    return {"erro": False, "periodo": periodo, "receitas": receitas}

@app.get("/historico_comparativo_receitas")
def get_historico_comparativo_receitas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_receitas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_receitas/{id}")
def get_historico_comparativo_receitas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_receitas WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_receitas")
async def salvar_comparativo_receitas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False, "mensagem": "Nenhum ID."}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cur.rowcount
    conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_receitas", response_class=HTMLResponse)
def serve_analise_comparativo_receitas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_receitas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)

@app.get("/relatorio_comparativo_receitas", response_class=HTMLResponse)
def serve_relatorio_comparativo_receitas():
    # Por enquanto, redireciona para o relatí³rio de centro de custos (ou crie um novo HTML)
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


@app.get("/api/comparativo_receitas_v2/{periodo}")
def api_comparativo_receitas_v2(periodo: str):
    import os, re

    upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"

    # Calcula o perí­odo anterior (mesmo trimestre do ano anterior)
    partes = periodo.split("-")
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

            grupos_nomes = ["RECEITAS PATRIMONIAIS", "TRANSFERíŠNCIAS CORRENTES", "RECEITAS DE SERVIí‡OS", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "RECEITAS DE CONTRIBUIí‡í•ES"]

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

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": "Dados não encontrados para o perí­odo atual."}

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {"orcado_total": 0, "realizado_total": 0, "percentual_total": 0, "grupos": [], "cores": []}
    }


@app.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os

    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo={periodo}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)  # Espera gráficos renderizarem
        page.evaluate("""() => {
            document.querySelectorAll('canvas').forEach(canvas => {
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.className = 'canvas-img';
                img.style.cssText = 'display: block; max-width: 100%; max-height: 240px; margin: 0 auto;';
                canvas.parentNode.insertBefore(img, canvas.nextSibling);
            });
        }""")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_receitas_{periodo}.pdf"}
    )


# ========== ROTAS DO COMPARATIVO DE DESPESAS ==========
@app.get("/api/comparativo_despesas_v2/{periodo}")
def api_comparativo_despesas_v2(periodo: str):
    import os, unicodedata
    upload_dir = r"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\uploads_raw"

    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0

    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0

    def normalizar(txt):
        return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8').strip().upper()

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

            # Lista fixa de cabeçalhos que NíƒO são contas analí­ticas
            cabecalhos = [
                "CREDITO DISPONIVEL", "CREDITO DISPONIVEL - DESPESA CORRENTE",
                "CREDITO DISPONIVEL - DESPESA CAPITAL",
                "PESSOAL E ENCARGOS SOCIAIS", "JUROS E ENCARGOS DA DIVIDA",
                "OUTRAS DESPESAS CORRENTES", "INVESTIMENTOS",
                "INVERSOES FINANCEIRAS", "AMORTIZACAO DA DIVIDA",
                "APLICACOES DIRETAS", "APLICACOES INDIRETAS",
                "OUTROS SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "DEMAIS SERVICOS - PESSOAS JURIDICAS",
                "APOSENTADORIAS DO RPPS", "PROVENTOS - PESSOAL CIVIL",
                "VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL",
                "OUTRAS DESPESAS VARIAVEIS - PESSOAL CIVIL - RGPS",
                "RESSARCIMENTO DE DESPESAS DE PESSOAL REQUISITADO",
                "JUROS SOBRE A DIVIDA POR CONTRATO",
                "JUROS DE SOBRE FORNECIMENTO DE BENS",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA FISICA",
                "OUTROS JUROS E ENCARGOS DE MORA",
                "DESPESAS DE EXERCICIOS ANTERIORES (JUROS E ENCARGOS DAS DIVIDAS)",
                "OUTRAS DESPESAS DE PESSOAL DECORRENTES DE CONTRATOS DE TERCEIROS",
                "OUTRAS DESPESAS CORRENTES - APLICACOES DIRETAS",
                "INVESTIMENTOS - APLICACOES DIRETAS",
                "INVERSOES FINANCEIRAS - APLICACOES DIRETAS",
                "AMORTIZACAO DA DIVIDA - APLICACOES DIRETAS",
                "TOTAL", "TOTAL GERAL"
            ]
            cabecalhos_norm = [normalizar(cg) for cg in cabecalhos]

            detalhes_temp = []

            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue

                nome_original = partes_linha[0].strip().strip('"')
                nome_norm = normalizar(nome_original)

                if not nome_original or len(nome_original) < 3: continue

                # Total Global
                if nome_norm == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])

                # Grupos contábeis
                grupos_alvo_norm = [
                    "PESSOAL E ENCARGOS SOCIAIS",
                    "JUROS E ENCARGOS DA DIVIDA",
                    "OUTRAS DESPESAS CORRENTES",
                    "INVESTIMENTOS",
                    "INVERSOES FINANCEIRAS",
                    "AMORTIZACAO DA DIVIDA"
                ]
                if nome_norm in grupos_alvo_norm:
                    if not any(g["nome"] == nome_original for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })

                # Detalhes: exclui cabeçalhos e pega o resto com valor > 0
                valor_emp = parse_valor(partes_linha[2])
                if valor_emp > 0 and nome_norm not in cabecalhos_norm:
                    # Exclui também linhas com "TOTAL" no nome (são somatí³rios)
                    if "TOTAL" not in nome_norm and "SUBTOTAL" not in nome_norm:
                        detalhes_temp.append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": valor_emp,
                            "percentual": parse_pct(partes_linha[3])
                        })

            # Ordena por empenhado desc e pega top 10
            detalhes_temp.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = detalhes_temp[:10]

            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": [], "detalhes": []
        }
    }
@app.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_despesas ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_despesas/{id}")
def get_historico_comparativo_despesas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_despesas WHERE id = ?", (id,))
    row = cur.fetchone(); conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_despesas")
async def salvar_comparativo_despesas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit(); conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
    conn.commit(); excluidos = cur.rowcount; conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_despesas", response_class=HTMLResponse)
def serve_analise_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)


@app.get("/gerar_pdf_integridade_matriz/{check_id}")
def gerar_pdf_integridade_matriz(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela de integridade com o ID passado
    url = f"http://127.0.0.1:9994/integridade?check={check_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=integridade_{check_id}.pdf"}
    )


@app.get("/gerar_pdf_conferencia/{check_id}")
def gerar_pdf_conferencia(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela de conferíªncia com o ID passado
    url = f"http://127.0.0.1:9994/conferencia_nova?check={check_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=conferencia_{check_id}.pdf"}
    )


@app.get("/gerar_pdf_comparativo_despesas")
def gerar_pdf_comparativo_despesas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo={periodo}&_t={int(time.time())}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_despesas_{periodo}.pdf"})


@app.get("/relatorio_comparativo_despesas", response_class=HTMLResponse)
def serve_relatorio_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatí³rio não encontrado</h1>", status_code=404)


# ========== ROTAS DE HISTí“RICO DESPESAS (FORí‡ADAS) ==========
@app.post("/api/comparativo_despesas_v2/{periodo}/salvar")
def rota_salvar_comparativo_despesas(periodo: str):
    import sqlite3, os, json
    from datetime import datetime

    dados = api_comparativo_despesas_v2(periodo)
    if dados.get("erro"): return {"erro": True, "mensagem": dados.get("mensagem")}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)

    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}

@app.delete("/historico_comparativo_despesas/{id}")
def rota_excluir_comparativo_despesas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_despesas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}
# ============================================================

@app.get("/gerar_pdf_composicao_receitas_despesas/{historico_id}")
def gerar_pdf_composicao_receitas_despesas(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela do relatí³rio passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_composicao_receitas_despesas?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=composicao_{historico_id}.pdf"}
    )

@app.get("/gerar_pdf_panorama/{historico_id}")
def gerar_pdf_panorama(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre a tela do panorama passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000) # Espera extra para gráficos renderizarem
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=panorama_{historico_id}.pdf"}
    )

@app.get("/relatorio_panorama")
def serve_relatorio_panorama():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "relatorio_panorama.html")
    return FileResponse(caminho)

@app.get("/gerar_pdf_centro_custos/{historico_id}")
def gerar_pdf_centro_custos(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time

    # Abre o relatí³rio v2 passando o ID do histí³rico
    url = f"http://127.0.0.1:9994/relatorio_centro_custos?historico_id={historico_id}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=centro_custos_{historico_id}.pdf"}
    )

@app.post("/salvar_conclusao_centro_custos/{historico_id}")
async def salvar_conclusao_centro_custos(historico_id: int, request: Request):
    import sqlite3, json, os
    try:
        data = await request.json()
        texto = data.get("texto", "")

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE id = ?", (historico_id,))
        row = cur.fetchone()

        if row:
            dados = json.loads(row[0])
            dados["conclusao_personalizada"] = texto
            cur.execute("UPDATE historico_centro_custos SET dados_json = ? WHERE id = ?", (json.dumps(dados), historico_id))
            conn.commit()
            conn.close()
            return {"erro": False, "mensagem": "Conclusão salva com sucesso!"}

        conn.close()
        return {"erro": True, "mensagem": "Histí³rico não encontrado."}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.get("/relatorio_comparativo_receitas_v2")
def serve_relatorio_receitas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Tenta v2, senão a versão sem v2
    for nome in ["relatorio_comparativo_receitas_v2.html", "relatorio_comparativo_receitas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatí³rio não encontrado"}


# ============================================================
# ROTAS DE SALVAR E EXCLUIR - COMPARATIVO DE RECEITAS
# ============================================================

@app.post("/api/comparativo_receitas_v2/{periodo}/salvar")
def salvar_comparativo_receitas(periodo: str):
    import sqlite3, os, json
    from datetime import datetime

    # Pega os dados atuais via API
    try:
        dados = api_comparativo_receitas_v2(periodo)
    except Exception as e:
        return {"erro": True, "mensagem": f"Erro ao buscar dados: {str(e)}"}

    if dados.get("erro"):
        return {"erro": True, "mensagem": dados.get("mensagem", "Dados não encontrados")}

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)

    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)",
                (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}


@app.delete("/historico_comparativo_receitas/{id}")
def excluir_historico_receitas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_receitas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}


@app.get("/relatorio_comparativo_despesas_v2")
def serve_relatorio_despesas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Procura o _v2 primeiro, senão o sem _v2
    for nome in ["relatorio_comparativo_despesas_v2.html", "relatorio_comparativo_despesas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatorio nao encontrado"}

@app.get("/download/pdf_csv/{tipo}")
async def download_pdf_csv(tipo: str, ano: int = Query(2026), periodo: str = Query("")):
    from fpdf import FPDF
    from fastapi.responses import Response
    import os

    # Mapeia o tipo para o nome do arquivo
    mapa = {
        "COMPARATIVO_DESPESAS": "COMPARATIVO_DESPESAS",
        "COMPARATIVO_RECEITAS": "COMPARATIVO_RECEITAS",
        "CENTRO_CUSTOS": "CENTRO_CUSTOS"
    }

    prefixo = mapa.get(tipo.upper(), tipo.upper())
    # Procura o arquivo mais recente com esse prefixo
    pasta = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
    arquivo = None
    for f in sorted(os.listdir(pasta), reverse=True):
        if f.startswith(prefixo) and f.endswith(".csv"):
            arquivo = os.path.join(pasta, f)
            break

    if not arquivo:
        return {"erro": True, "mensagem": f"Arquivo CSV para {tipo} não encontrado."}

    # Líª o CSV
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except:
        with open(arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()

    # Gera o PDF
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Tí­tulo
    pdf.set_font("Helvetica", "B", 16)
    titulo = tipo.replace("_", " ").title()
    pdf.cell(0, 10, f"Relatí³rio - {titulo}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Arquivo: {os.path.basename(arquivo)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Cabeçalho da tabela
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(0, 114, 186)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "Descrição", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Orçado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Realizado", border=1, fill=True, align="C")
    pdf.cell(30, 8, "%", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    # Dados (pula linhas de cabeçalho)
    count = 0
    for linha in linhas:
        if ";" not in linha: continue
        partes = linha.strip().split(";")
        if len(partes) < 3: continue
        nome = partes[0].strip().strip('"')[:50]
        if not nome or "COFEN" in nome.upper() or "PERIODO" in nome.upper(): continue
        orcado = partes[1].strip() if len(partes) > 1 else ""
        realizado = partes[2].strip() if len(partes) > 2 else ""
        pct = partes[3].strip() if len(partes) > 3 else ""
        if not orcado or orcado == "Orçado": continue

        pdf.set_font("Helvetica", "", 7)
        pdf.cell(80, 6, nome, border=1)
        pdf.cell(30, 6, orcado, border=1, align="R")
        pdf.cell(30, 6, realizado, border=1, align="R")
        pdf.cell(30, 6, pct, border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        count += 1
        if count > 60: break

    out = pdf.output()
    return Response(content=bytes(out), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="relatorio_{tipo}_{ano}.pdf"'})


# ============================================================
# ROTAS DE CONFIGURACOES (CADASTRO DA ENTIDADE)
# ============================================================

@app.get('/api/configuracoes/entidade')
async def obter_entidade():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
    cursor = conn.cursor()

    # Cria a tabela se nao existir
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()

    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"razao_social": "", "nome_fantasia": "", "cnpj": "", "endereco": "", "email": "", "telefone": "", "contador_nome": "", "contador_crc": "", "contador_uf": "", "contador_cpf": "", "contador_email": "", "logo_path": ""}

    # Acessa pelo nome da coluna (evita erro de indice desalinhado)
    def get_col(nome):
        try:
            return row[nome] or ""
        except Exception:
            return ""

    return {
        "razao_social": get_col("razao_social"),
        "nome_fantasia": get_col("nome_fantasia"),
        "cnpj": get_col("cnpj"),
        "endereco": get_col("endereco"),
        "email": get_col("email"),
        "telefone": get_col("telefone"),
        "contador_nome": get_col("contador_nome"),
        "contador_crc": get_col("contador_crc"),
        "contador_uf": get_col("contador_uf"),
        "contador_cpf": get_col("contador_cpf"),
        "contador_email": get_col("contador_email"),
        "logo_path": get_col("logo_path")
    }

@app.post('/api/configuracoes/entidade')
async def salvar_entidade(request: Request):
    import sqlite3
    from datetime import datetime
    try:
        body = await request.json()
    except Exception:
        return {'ok': False, 'mensagem': 'Dados invalidos.'}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pc_storage', 'banco_dados.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT)''')
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('DELETE FROM configuracoes_entidade')
    cursor.execute('''INSERT INTO configuracoes_entidade
        (razao_social, nome_fantasia, cnpj, endereco, email, telefone, contador_nome, contador_crc, contador_uf, contador_cpf, contador_email, data_atualizacao, logo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        body.get('razao_social', ''),
        body.get('nome_fantasia', ''),
        body.get('cnpj', ''),
        body.get('endereco', ''),
        body.get('email', ''),
        body.get('telefone', ''),
        body.get('contador_nome', ''),
        body.get('contador_crc', ''),
        body.get('contador_uf', ''),
        body.get('contador_cpf', ''),
        body.get('contador_email', ''),
        data_agora,
        body.get('logo_path', '')))
    conn.commit()
    conn.close()
    return {'ok': True, 'mensagem': 'Configuracoes salvas com sucesso!'}

@app.get('/configuracoes')
async def serve_configuracoes():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pc_frontend', 'configuracoes.html')
    return FileResponse(caminho, headers={'Cache-Control': 'no-store, no-cache, must-revalidate'})


@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        msg = "Coluna logo_path adicionada."
    except Exception as e:
        msg = f"Ja existe ou erro: {str(e)[:50]}"
    conn.close()
    return {"ok": True, "mensagem": msg}


@app.post("/api/configuracoes/logo")
async def upload_logo(file: UploadFile = File(...)):
    import os, uuid, sqlite3
    from fastapi import HTTPException

    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PNG ou JPG.")

    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)

    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(await file.read())

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()

    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    cursor.execute("SELECT COUNT(*) FROM configuracoes_entidade")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', ?)", (nome_arquivo,))
    else:
        cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (nome_arquivo,))
    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}

@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        msg = "Coluna logo_path adicionada."
    except Exception as e:
        msg = "Coluna ja existe ou erro: " + str(e)[:50]
    conn.close()
    return {"ok": True, "mensagem": msg}


app.mount("/static_logos", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")), name="static_logos")


# ============================================================
# ROTAS DO RELATORIO CONSOLIDADO
# ============================================================


@app.get("/historico_relatorio_consolidado")
async def get_hist_consolidado():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_relatorio_consolidado ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.delete("/excluir_relatorio_consolidado/{id}")
async def excluir_relatorio_consolidado(id: int):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/relatorio_consolidado")
async def serve_relatorio_consolidado():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})


# ============================================================
# API DA ANALISE BP (Balanco Patrimonial)
# ============================================================


@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob, unicodedata
    from fastapi import HTTPException

    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")

    ano_atual = p_limpo.split("_")[0]
    candidatos = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_atual}*.csv"))
    if not candidatos:
        return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    caminho = candidatos[0]

    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").replace("C", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0

    def remover_acentos(s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').upper().strip()

    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            for row in csv.reader(f, delimiter=";"):
                linhas.append(row)

        # Ativo: Col0 (esp), Col1 (atual), Col2 (anterior)
        # Passivo: Col3 (esp), Col4 (atual), Col5 (anterior)

        def buscar_ativo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 2 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1]), limpar(p[2])
            return 0.0, 0.0

        def buscar_passivo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 5 and termo_norm in remover_acentos(str(p[3])):
                    return limpar(p[4]), limpar(p[5])
            return 0.0, 0.0

        # Busca os valores (atual, anterior)
        ativo_circ_at, ativo_circ_ant = buscar_ativo("ATIVO CIRCULANTE")
        caixa_at, caixa_ant = buscar_ativo("CAIXA E EQUIVALENTES")
        # Busca o Superávit Financeiro na coluna 3 (valor) da linha que contém "SUPERVIT" ou "SUPERAVIT"
        superavit_at = 0.0
        superavit_ant = 0.0
        for p in linhas:
            if len(p) > 3 and ("SUPERVIT" in remover_acentos(str(p[0])).upper() or "SUPERAVIT" in remover_acentos(str(p[0])).upper()):
                try:
                    superavit_at = limpar(p[3])
                    superavit_ant = limpar(p[4]) if len(p) > 4 else 0.0
                except:
                    pass
                break
        estoques_at, estoques_ant = buscar_ativo("ESTOQUES")
        creditos_at, creditos_ant = buscar_ativo("CRí‰DITOS A CURTO PRAZO")
        ativo_nao_circ_at, ativo_nao_circ_ant = buscar_ativo("ATIVO NíƒO CIRCULANTE")
        ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZíVEL A LONGO PRAZO")
        imobilizado_at, imobilizado_ant = buscar_ativo("IMOBILIZADO")

        passivo_circ_at, passivo_circ_ant = buscar_passivo("PASSIVO CIRCULANTE")
        passivo_nao_circ_at, passivo_nao_circ_ant = buscar_passivo("PASSIVO NAO-CIRCULANTE")
        pl_at, pl_ant = buscar_passivo("RESULTADOS ACUMULADOS")

        # Total do Ativo
        total_ativo_at = ativo_circ_at + ativo_nao_circ_at
        total_ativo_ant = ativo_circ_ant + ativo_nao_circ_ant

        # PASSIVO TOTAL = Passivo Circulante + Passivo Nao Circulante
        passivo_total_at = passivo_circ_at + passivo_nao_circ_at
        passivo_total_ant = passivo_circ_ant + passivo_nao_circ_ant

        # TOTAL DO PASSIVO = Passivo Total + Patrimonio Liquido
        total_passivo_at = passivo_total_at + pl_at
        total_passivo_ant = passivo_total_ant + pl_ant

        dados = {
            "ativo_circulante": {"atual": ativo_circ_at, "anterior": ativo_circ_ant},
            "caixa": {"atual": caixa_at, "anterior": caixa_ant},
            "superavit_financeiro": {"atual": superavit_at, "anterior": superavit_ant},
            "estoques": {"atual": estoques_at, "anterior": estoques_ant},
            "creditos": {"atual": creditos_at, "anterior": creditos_ant},
            "ativo_nao_circulante": {"atual": ativo_nao_circ_at, "anterior": ativo_nao_circ_ant},
            "ativo_realizavel": {"atual": ativo_realizavel_at, "anterior": ativo_realizavel_ant},
            "imobilizado": {"atual": imobilizado_at, "anterior": imobilizado_ant},
            "total_ativo": {"atual": total_ativo_at, "anterior": total_ativo_ant},
            "passivo_circulante": {"atual": passivo_circ_at, "anterior": passivo_circ_ant},
            "passivo_nao_circulante": {"atual": passivo_nao_circ_at, "anterior": passivo_nao_circ_ant},
            "passivo_total": {"atual": passivo_total_at, "anterior": passivo_total_ant},
            "patrimonio_liquido": {"atual": pl_at, "anterior": pl_ant},
            "total_passivo": {"atual": total_passivo_at, "anterior": total_passivo_ant},
        }

        return {"erro": False, "dados": dados}

    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise_bp")
async def serve_analise_bp():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_bp.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

@app.post("/salvar_analise_bp/{periodo}")
async def salvar_analise_bp(periodo: str):
    import sqlite3, json, os
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    # Chama a API para pegar os dados atuais
    try:
        dados = await api_analise_bp(periodo)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular BP: {e}"}

    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_bp (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Analise BP salva com sucesso!"}

@app.get("/historico_analise_bp")
async def get_hist_bp():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_analise_bp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_analise_bp/{id}")
async def get_bp_id(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"erro": "nao encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

@app.delete("/excluir_analise_bp/{id}")
async def excluir_bp(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_analise_bp WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/gerar_pdf_analise_bp/{id}")
async def gerar_pdf_analise_bp(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    from datetime import datetime

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_bp WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)

    periodo, data_geracao, res_json = row
    try:
        dados = json.loads(res_json)
    except Exception:
        dados = {}

    d = dados.get("dados", {})

    def fmt(v):
        if v is None: return "0,00"
        s = f"{v:,.2f}"
        # Formato: 1,234,567.89 -> 1.234.567,89
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANALISE DO BALANCO PATRIMONIAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Periodo: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    col_w = [55, 35, 35, 25, 25]
    headers = ["Conta", "Periodo Atual (R$)", "Periodo Anterior (R$)", "Var. (%)", "AV (%)"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)

    def linha(label, va, vb, base_av=0):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")

        # Variação (%)
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")

        # Análise Vertical (AV %)
        if base_av and base_av != 0:
            av = (va / base_av) * 100
            av_str = f"{av:,.2f}%".replace(".", ",")
        else:
            av_str = "-"
        pdf.cell(col_w[4], 7, av_str, border=1, align="R")

        pdf.ln()

    total_ativo_val = d.get('total_ativo', {}).get('atual', 0) or 0

    total_passivo_val = d.get('total_passivo', {}).get('atual', 0) or 0


    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0), total_ativo_val)
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0), total_ativo_val)
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0), total_ativo_val)
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0), total_ativo_val)
    linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0), total_ativo_val)
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0), total_ativo_val)
    linha("TOTAL DO ATIVO", total_ativo_val, d.get("total_ativo", {}).get("anterior", 0), total_ativo_val)
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0), total_passivo_val)
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0), total_passivo_val)
    linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0), total_passivo_val)
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0), total_passivo_val)
    linha("TOTAL DO PASSIVO", total_passivo_val, d.get("total_passivo", {}).get("anterior", 0), total_passivo_val)
    linha("Superávit Financeiro", 63825301.60, 114355899.33)

    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_BP_{periodo}.pdf"})


# =========================================================
# ROTAS DE LIQUIDEZ (adicionadas automaticamente)
# =========================================================


@app.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str):
    dados = _calc_liquidez(periodo)
    if not dados:
        return {"erro": True, "mensagem": "Balanco Patrimonial nao encontrado para este periodo."}
    return dados

@app.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez_rota(periodo: str):
    try:
        dados = _calc_liquidez(periodo)
        if not dados:
            return {"erro": True, "mensagem": "Sem dados para salvar."}
        import sqlite3 as _sq, json as _js, datetime as _dt
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = _sq.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = _dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, _js.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Liquidez salva com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@app.get("/historico_liquidez")
async def listar_historico_liquidez():
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cur.execute("SELECT id, periodo, data_geracao FROM historico_liquidez ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]


@app.get("/historico_liquidez/{id}")
async def get_liquidez_id(id: int):
    import sqlite3 as _sq, json as _js
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    dados = _js.loads(row[2])
    dados["_periodo_hist"] = row[0]
    dados["_data_hist"] = row[1]
    return dados


@app.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int):
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_liquidez WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/gerar_pdf_liquidez/{id}")
def gerar_pdf_liquidez(id: int):
    import sqlite3 as _sq
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao = row
    dados = _calc_liquidez(periodo)
    if not dados:
        return Response(content="Balanco Patrimonial nao encontrado.", status_code=404, media_type="text/plain")

    liq      = dados.get("liquidez", {})           or {}
    est      = dados.get("estrutura", {})          or {}
    liq_ant  = dados.get("liquidez_anterior", {})  or {}
    est_ant  = dados.get("estrutura_anterior", {}) or {}
    val      = dados.get("valores", {})            or {}
    val_ant  = dados.get("valores_anterior", {})   or {}

    def fmt_moeda(v):
        if v is None: return "R$ 0,00"
        try:
            return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(v)

    def fmt_num(v):
        if v is None: return "-"
        return str(v).replace(".", ",")

    def var_pct(atual, anterior):
        try:
            a = float(str(atual).replace(".", "").replace(",", "."))
            p = float(str(anterior).replace(".", "").replace(",", "."))
            if p == 0: return "-"
            return f"{((a-p)/p)*100:+.2f}%".replace(".", ",")
        except:
            return "-"

    # Paisagem (Landscape)
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    # --- TITULO PRINCIPAL ---
    pdf.set_fill_color(0, 45, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(277, 10, "Indicadores de Liquidez e Estrutura Patrimonial (Atual x Anterior)", border=0, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # --- TABELA 1: RESUMO ---
    # Larguras: 100 + 50 + 50 + 77 = 277mm
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 70, 140)
    pdf.cell(100, 7, "INDICADOR", border=0, fill=True)
    pdf.cell(50, 7, "ATUAL", border=0, align="C", fill=True)
    pdf.cell(50, 7, "ANTERIOR", border=0, align="C", fill=True)
    pdf.cell(77, 7, "VAR. (%)", border=0, align="C", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def sub_header(texto):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(0, 45, 90)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(277, 7, texto, border=0, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)

    def linha_resumo(label, va, vp, v_var):
        pdf.cell(100, 7, label, border="B")
        pdf.cell(50, 7, va, border="B", align="C")
        pdf.cell(50, 7, vp, border="B", align="C")
        pdf.cell(77, 7, v_var, border="B", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    sub_header("LIQUIDEZ")
    for label, chave in [("Liquidez Imediata", "liquidez_imediata"), ("Liquidez Corrente", "liquidez_corrente"), ("Liquidez Seca", "liquidez_seca"), ("Liquidez Geral", "liquidez_geral")]:
        va = fmt_num(liq.get(chave, "-"))
        vp = fmt_num(liq_ant.get(chave, "-"))
        linha_resumo(label, va, vp, var_pct(va, vp))

    sub_header("ESTRUTURA PATRIMONIAL")
    for label, chave in [("Endividamento Geral", "endividamento_geral"), ("Part. Capital de Terceiros", "part_capital_terceiros"), ("Imobilização do PL", "imobilizacao_pl")]:
        va = fmt_num(est.get(chave, "-"))
        vp = fmt_num(est_ant.get(chave, "-"))
        linha_resumo(label, va + "%", vp + "%", var_pct(va, vp))

    pdf.ln(8)

    # --- TABELA 2: MEMí“RIA DE CíLCULO ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(277, 6, "Memí³ria de Cálculo (Atual x Anterior)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Larguras ajustadas: 35 + 55 + 71 + 20 + 71 + 25 = 277mm
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(0, 70, 140)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 7, "INDICE", border=0, align="C", fill=True)
    pdf.cell(55, 7, "Fí“RMULA", border=0, align="C", fill=True)
    pdf.cell(71, 7, "CíLCULO (ATUAL)", border=0, align="C", fill=True)
    pdf.cell(20, 7, "RESULTADO", border=0, align="C", fill=True)
    pdf.cell(71, 7, "CíLCULO (ANTERIOR)", border=0, align="C", fill=True)
    pdf.cell(25, 7, "RESULTADO", border=0, align="C", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 6)

    def draw_row_memoria(label, formula, calc_a, res_a, calc_p, res_p):
        h = 7
        pdf.cell(35, h, label, border="B", align="L")
        pdf.cell(55, h, formula, border="B", align="L")
        pdf.cell(71, h, calc_a, border="B", align="L")
        pdf.cell(20, h, res_a, border="B", align="C")
        pdf.cell(71, h, calc_p, border="B", align="L")
        pdf.cell(25, h, res_p, border="B", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    draw_row_memoria(
        "Liquidez Imediata", "Caixa / Passivo Circ.",
        f"{fmt_moeda(val.get('caixa'))} / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_imediata", "-")),
        f"{fmt_moeda(val_ant.get('caixa'))} / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_imediata", "-"))
    )
    draw_row_memoria(
        "Liquidez Corrente", "Ativo Circ. / Passivo Circ.",
        f"{fmt_moeda(val.get('ativo_circulante'))} / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_corrente", "-")),
        f"{fmt_moeda(val_ant.get('ativo_circulante'))} / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_corrente", "-"))
    )
    draw_row_memoria(
        "Liquidez Seca", "(Ativo Circ. - Estoques) / Passivo Circ.",
        f"({fmt_moeda(val.get('ativo_circulante'))} - {fmt_moeda(val.get('estoques'))}) / {fmt_moeda(val.get('passivo_circulante'))}", str(liq.get("liquidez_seca", "-")),
        f"({fmt_moeda(val_ant.get('ativo_circulante'))} - {fmt_moeda(val_ant.get('estoques'))}) / {fmt_moeda(val_ant.get('passivo_circulante'))}", str(liq_ant.get("liquidez_seca", "-"))
    )
    draw_row_memoria(
        "Liquidez Geral", "(AC + Realiz. LP) / (PC + P. N. Circ.)",
        f"({fmt_moeda(val.get('ativo_circulante'))} + {fmt_moeda(val.get('realizavel_lp'))}) / ({fmt_moeda(val.get('passivo_circulante'))} + {fmt_moeda(val.get('passivo_nao_circulante'))})", str(liq.get("liquidez_geral", "-")),
        f"({fmt_moeda(val_ant.get('ativo_circulante'))} + {fmt_moeda(val_ant.get('realizavel_lp'))}) / ({fmt_moeda(val_ant.get('passivo_circulante'))} + {fmt_moeda(val_ant.get('passivo_nao_circulante'))})", str(liq_ant.get("liquidez_geral", "-"))
    )
    draw_row_memoria(
        "Endividamento Geral", "Passivo Total / Ativo Total",
        f"{fmt_moeda(val.get('passivo_total'))} / {fmt_moeda(val.get('ativo_total'))}", str(est.get("endividamento_geral", "-")) + "%",
        f"{fmt_moeda(val_ant.get('passivo_total'))} / {fmt_moeda(val_ant.get('ativo_total'))}", str(est_ant.get("endividamento_geral", "-")) + "%"
    )
    draw_row_memoria(
        "Part. Capital Terceiros", "Passivo Total / PL",
        f"{fmt_moeda(val.get('passivo_total'))} / {fmt_moeda(val.get('patrimonio_liquido'))}", str(est.get("part_capital_terceiros", "-")) + "%",
        f"{fmt_moeda(val_ant.get('passivo_total'))} / {fmt_moeda(val_ant.get('patrimonio_liquido'))}", str(est_ant.get("part_capital_terceiros", "-")) + "%"
    )
    draw_row_memoria(
        "Imobilização do PL", "Imobilizado / PL",
        f"{fmt_moeda(val.get('imobilizado'))} / {fmt_moeda(val.get('patrimonio_liquido'))}", str(est.get("imobilizacao_pl", "-")) + "%",
        f"{fmt_moeda(val_ant.get('imobilizado'))} / {fmt_moeda(val_ant.get('patrimonio_liquido'))}", str(est_ant.get("imobilizacao_pl", "-")) + "%"
    )

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=liquidez_{id}.pdf"},
    )
# =========================================================
# FIM DAS ROTAS DE LIQUIDEZ
# =========================================================


@app.post("/excluir_panorama_multiplos")
async def excluir_panorama_multiplos(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids_brutos = dados.get("ids", [])

        if not ids_brutos:
            return {"erro": True, "mensagem": "Nenhum ID enviado"}

        # Garante que todos são inteiros (para o SQLite)
        ids = [int(i) for i in ids_brutos if str(i).strip().isdigit()]

        if not ids:
            return {"erro": True, "mensagem": "IDs inválidos"}

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_panorama WHERE id IN ({placeholders})", ids)
        excluidos = cursor.rowcount
        conn.commit()
        conn.close()

        return {"ok": True, "mensagem": f"{excluidos} itens excluí­dos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    modulos = {
        "analise_bp": "historico_analise_bp",
        "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial",
        "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf",
        "comparativo_receitas": "historico_comparativo_receitas",
        "comparativo_despesas": "historico_comparativo_despesas",
        "panorama": "historico_panorama",
        "liquidez": "historico_liquidez",
        "integridade": "historico_integridade_matriz",
        "conferencia": "historico_conferencia",
        "custo_pessoal": "historico_custo_pessoal",
        "centro_custos": "historico_centro_custos"
    }

    nomes_amigaveis = {
        "analise_bp": "Análise BP",
        "analise_dfc": "Análise DFC",
        "analise_patrimonial": "Análise Patrimonial (DVP)",
        "analise_orcamentaria": "Análise Orçamentária (BO)",
        "analise_financeira_bf": "Análise Financeira (BF)",
        "comparativo_receitas": "Comparativo de Receitas",
        "comparativo_despesas": "Comparativo de Despesas",
        "panorama": "Panorama de Resultados",
        "liquidez": "índices de Liquidez",
        "integridade": "Integridade entre Demonstraçíµes",
        "conferencia": "Conferíªncia das Demonstraçíµes",
        "custo_pessoal": "Custo de Pessoal",
        "centro_custos": "Análise por Centro de Custos"
    }

    encontrados = {}
    faltando = []

    for chave, tabela in modulos.items():
        try:
            # Tenta buscar a coluna resultado_json (padrão)
            # Se falhar, tenta dados_json (como nos comparativos)
            try:
                cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                row = cursor.fetchone()
            except sqlite3.OperationalError:
                cursor.execute(f"SELECT dados_json, data_geracao FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                row = cursor.fetchone()

            if row:
                try:
                    dados = json.loads(row[0])
                except:
                    dados = {"raw": row[0]}
                encontrados[chave] = {
                    "nome": nomes_amigaveis[chave],
                    "data_geracao": row[1],
                    "dados": dados
                }
            else:
                faltando.append({"chave": chave, "nome": nomes_amigaveis[chave]})
        except Exception as e:
            faltando.append({"chave": chave, "nome": nomes_amigaveis[chave], "erro": str(e)})

    conn.close()

    return {
        "periodo": periodo,
        "encontrados": encontrados,
        "faltando": faltando,
        "status": "ok" if len(faltando) == 0 else "faltando",
        "total_modulos": len(modulos),
        "total_encontrados": len(encontrados),
        "total_faltando": len(faltando)
    }

@app.post("/salvar_relatorio_consolidado/{periodo}")
async def salvar_relatorio_consolidado_novo(periodo: str):
    import sqlite3, os, json
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    # Chama a API para coletar os dados
    dados_api = await api_relatorio_consolidado_novo(periodo)

    if dados_api["status"] == "faltando":
        return {
            "ok": False,
            "mensagem": f"Faltam {len(dados_api['faltando'])} mí³dulo(s) para consolidar.",
            "faltando": dados_api["faltando"]
        }

    dados_consolidados = {
        "periodo": periodo,
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "dados": dados_api["encontrados"]
    }

    cursor.execute("INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, dados_consolidados["data_geracao"], json.dumps(dados_consolidados, ensure_ascii=False)))
    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Relatí³rio consolidado salvo com sucesso!", "dados": dados_consolidados}


@app.get("/historico_relatorio_consolidado/{id}")
async def get_historico_consolidado(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"erro": "Histí³rico não encontrado"}

    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": json.loads(row[2])
    }


@app.post("/excluir_multiplos_relatorio_consolidado")
async def excluir_multiplos_relatorio_consolidado(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids:
            return {"erro": True, "mensagem": "Nenhum ID válido"}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_relatorio_consolidado WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluí­dos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@app.get("/api/observacoes_consolidado/{relatorio_id}")
async def get_observacoes(relatorio_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, item, texto FROM observacoes_consolidado WHERE relatorio_id = ?", (relatorio_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "item": r[1], "texto": r[2]} for r in rows]

@app.post("/api/observacoes_consolidado/{relatorio_id}")
async def post_observacao(relatorio_id: int, request: Request):
    import sqlite3, os
    from datetime import datetime
    dados = await request.json()
    item = dados.get("item", "")
    texto = dados.get("texto", "")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO observacoes_consolidado (relatorio_id, item, texto, data_criacao) VALUES (?, ?, ?, ?)",
        (relatorio_id, item, texto, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    return {"ok": True}

@app.put("/api/observacoes_consolidado/{obs_id}")
async def put_observacao(obs_id: int, request: Request):
    import sqlite3, os
    from datetime import datetime
    dados = await request.json()
    texto = dados.get("texto", "")
    item = dados.get("item", "")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE observacoes_consolidado SET item = ?, texto = ?, data_criacao = ? WHERE id = ?",
        (item, texto, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), obs_id)
    )
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/observacoes_consolidado/{obs_id}")
async def del_observacao(obs_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM observacoes_consolidado WHERE id = ?", (obs_id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/conclusao_consolidado/{relatorio_id}")
async def get_conclusao(relatorio_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto FROM conclusao_consolidado WHERE relatorio_id = ?", (relatorio_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "texto": row[1]}
    return {"id": None, "texto": ""}

@app.post("/api/conclusao_consolidado/{relatorio_id}")
async def post_conclusao(relatorio_id: int, request: Request):
    import sqlite3, os
    from datetime import datetime
    dados = await request.json()
    texto = dados.get("texto", "")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conclusao_consolidado WHERE relatorio_id = ?", (relatorio_id,))
    cursor.execute(
        "INSERT INTO conclusao_consolidado (relatorio_id, texto, data_criacao) VALUES (?, ?, ?)",
        (relatorio_id, texto, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/conclusao_consolidado/{relatorio_id}")
async def del_conclusao(relatorio_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conclusao_consolidado WHERE relatorio_id = ?", (relatorio_id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import sqlite3, json, os, base64, re

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    dados = json.loads(res_json).get("dados", {})

    # Injeção da DMPL
    try:
        cursor.execute("SELECT resultado_json FROM historico_analise_dmpl ORDER BY id DESC LIMIT 1")
        row_dmpl = cursor.fetchone()
        if row_dmpl:
            dados["dmpl"] = json.loads(row_dmpl[0])
    except Exception as e:
        print("Erro ao injetar DMPL:", e)
    
    # Busca observaçíµes, conclusão e contador
    cursor.execute("SELECT item, texto FROM observacoes_consolidado WHERE relatorio_id = ?", (id,))
    obs_rows = cursor.fetchall()
    cursor.execute("SELECT texto FROM conclusao_consolidado WHERE relatorio_id = ?", (id,))
    row_concl = cursor.fetchone()
    cursor.execute("SELECT contador_nome, contador_crc, contador_uf, contador_cpf FROM configuracoes_entidade LIMIT 1")
    row_contador = cursor.fetchone()
    conn.close()

    # Carrega o template
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Carrega o logo em base64
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "logo-cofen.png")
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()

    # Substitui os dados no template
    dados_json_str = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    html_final = (template
        .replace("{dados_json}", dados_json_str)
        .replace("{periodo}", periodo)
        .replace("{data_geracao}", data_geracao)
        .replace('src="logo"', 'src="' + logo_base64 + '"'))

    # Remove textos fixos indesejados
    html_final = html_final.replace('Conclusão da análise contábil.', '')
    html_final = html_final.replace('Análise Concluí­da', '')
    html_final = html_final.replace('Os dados foram consolidados com sucesso.', '')

    # Injeta observaçíµes
    if obs_rows:
        obs_js = "\n<script>\ndocument.addEventListener('DOMContentLoaded', function() {\n  setTimeout(function() {\n    var titulos = Array.from(document.querySelectorAll('h2.secao-titulo'));\n"
        for item, texto in obs_rows:
            texto_escapado = texto.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
            obs_js += "    (function() {\n      var idx = titulos.findIndex(function(h) { return h.innerText.trim().startsWith('" + item + ". '); });\n      if (idx >= 0) {\n        var div = document.createElement('div');\n        div.style.cssText = 'background:#E3F2FD; border-left:4px solid #2196F3; padding:10px; margin:15px 0 20px 0; font-size:11px; color:#0D47A1;';\n        div.innerHTML = '" + texto_escapado + "';\n        var proximo = titulos[idx + 1];\n        if (proximo) { proximo.parentNode.insertBefore(div, proximo); } else { titulos[idx].parentNode.appendChild(div); }\n      }\n    })();\n"
        obs_js += "  }, 500);\n});\n</script>\n"
        html_final = html_final.replace('</body>', obs_js + '</body>')

    # Injeta conclusão (com formatação ABNT)
    if row_concl and row_concl[0]:
        _txt = row_concl[0]
        _txt = _txt.replace(chr(10), '<br><br>')
        _txt = re.sub(r'\s+(\d+\.)\s+', r'<br><br><b>\1</b> ', _txt)
        _txt = re.sub(r'\s+(Recomenda-se:)', r'<br><br><b>\1</b>', _txt)
        _txt = re.sub(r'\s+(Conclusão:)', r'<br><br><b>\1</b>', _txt)
        _txt = re.sub(r'(<br><br>)+', '<br><br>', _txt)
        
        conclusao_html = '<div style="margin-top: 40px; padding: 20px; background: #f4f7f9; border-left: 5px solid #003366; font-size: 11px; line-height: 1.5; text-align: justify; color: #333; page-break-inside: avoid;">'
        conclusao_html += '<div style="font-family: Arial, sans-serif;">' + _txt + '</div></div>'
        html_final = html_final.replace('</body>', conclusao_html + '</body>')

                # Injeta dados do contador (Com máscara LGPD no CPF)
    if row_contador:
        nome = row_contador[0] or ""
        crc_bruto = row_contador[1] or ""
        uf_banco = row_contador[2] or ""
        cpf_bruto = row_contador[3] or ""
        
        # Limpa o CRC (apenas A-Z0-9)
        crc_limpo = re.sub(r'[^A-Z0-9]', '', crc_bruto.upper())
        
        # Remove a UF do iní­cio do CRC (se existir)
        if len(crc_limpo) >= 3 and crc_limpo[:2].isalpha():
            numero_crc = crc_limpo[2:]
        else:
            numero_crc = crc_limpo
            
        # Formata: Numero/UF (ex: 066005O8T/DF)
        crc_formatado = f"{numero_crc}/{uf_banco.upper()}"

        # MíSCARA LGPD DO CPF: ***.212.***-**
        # Remove formatação e mantém apenas dí­gitos
        cpf_limpo = re.sub(r'[^0-9]', '', cpf_bruto)
        if len(cpf_limpo) == 11:
            cpf_formatado = f"***.{cpf_limpo[3:6]}.***-**"
        else:
            cpf_formatado = cpf_bruto  # Fallback se não for 11 dí­gitos

        dados_contador = f"""
        <div style="margin-top:40px; text-align:center; font-size:11px; page-break-inside: avoid;">
            <p style="margin:0;"><b>{nome}</b></p>
            <p style="margin:0;">CRC: {crc_formatado} - CPF: {cpf_formatado}</p>
        </div>
        """
        html_final = html_final.replace('</body>', dados_contador + '</body>')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_final, wait_until="networkidle")
        page.wait_for_timeout(1500)
        pdf_bytes = page.pdf(format="A4", landscape=False, print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=relatorio_consolidado_" + str(id) + ".pdf"})

@app.get("/gerar_pdf_analise_dmpl/{id}")
def gerar_pdf_analise_dmpl(id: int):
    import sqlite3 as _sq, json as _js
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_analise_dmpl WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    dados = _js.loads(res_json)
    
    linhas = dados.get("dados", [])
    inicio_dados = 6 # Pula o cabecalho do COFEN
    linhas_validas = [l for l in linhas[inicio_dados:] if len(l) >= 3]

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(5, 5, 5)
    pdf.set_auto_page_break(auto=False)

    # CABECALHO PRINCIPAL
    pdf.set_fill_color(0, 45, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(287, 10, "DMPL - Demonstração das Mutaçíµes do Patrimí´nio Lí­quido", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.ln(1)
    pdf.cell(0, 4, f"Perí­odo: {periodo} | Data de Geração: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(3)

    # CABECALHO DA TABELA
    headers = [
        ("Especificação", 72, "L"),
        ("Patrimí´nio Social", 26, "R"),
        ("Adiant. Capital", 26, "R"),
        ("Reservas Capital", 26, "R"),
        ("Ajustes Avaliação", 26, "R"),
        ("Reservas Lucros", 26, "R"),
        ("Demais Reservas", 26, "R"),
        ("Result. Acumulados", 26, "R"),
        ("Total", 33, "R")
    ]
    
    # AUTO AJUSTE PARA CABER EM 1 PAGINA
    # A pagina paisagem tem 210mm de altura. Descontando margens e cabecalho, sobram ~165mm para a tabela.
    altura_disponivel = 165 
    qtd_linhas = len(linhas_validas) + 1 # +1 pelo cabecalho da tabela
    altura_linha = altura_disponivel / qtd_linhas
    
    # Limita a altura para nao ficar gigante nem minuscula
    altura_linha = min(8, max(2.5, altura_linha))
    tam_fonte = 6 if altura_linha >= 4 else 5

    pdf.set_font("Helvetica", "B", 6)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    
    for h_txt, h_w, h_align in headers:
        pdf.cell(h_w, altura_linha + 1, h_txt, border=1, align="C", fill=True)
    pdf.ln()

    # DADOS DA TABELA
    pdf.set_text_color(0, 0, 0)
    
    for linha in linhas_validas:
        while len(linha) < 9:
            linha.append("")
            
        is_total = "Total" in linha[0] or "Saldo" in linha[0] or "Saldos finais" in linha[0].lower()
        is_header = linha[0].strip() != "" and all(not str(c).strip() for c in linha[1:])
        
        if is_header:
            pdf.set_font("Helvetica", "B", tam_fonte)
            pdf.set_fill_color(230, 236, 245)
            pdf.cell(287, altura_linha, linha[0], border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", tam_fonte)
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_font("Helvetica", "B" if is_total else "", tam_fonte)
            
            fill = True if is_total else False
            if is_total:
                pdf.set_fill_color(245, 247, 250)
                
            for j in range(9):
                w = headers[j][1]
                align = "L" if j == 0 else "R"
                txt = str(linha[j]).strip()
                if len(txt) > 50 and j == 0:
                    txt = txt[:47] + "..."
                pdf.cell(w, altura_linha, txt, border=1, align=align, fill=fill)
            pdf.ln()

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=dmpl_{id}.pdf"},
    )


# ========================================================
# Mí“DULO DE NOTAS EXPLICATIVAS (padrão Relatí³rio Consolidado)
# ========================================================

# --- Tabelas do banco (criadas no primeiro uso) ---
def _init_notas_tables():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_notas_explicativas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS observacoes_notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, relatorio_id INTEGER, item TEXT, texto TEXT, data_criacao TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS conclusao_notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, relatorio_id INTEGER, texto TEXT, data_criacao TEXT)""")
    conn.commit()
    conn.close()

_init_notas_tables()

# --- Rota para abrir a tela ---
@app.get("/notas_explicativas")
async def serve_notas_explicativas():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "notas_explicativas.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

# --- Coleta dados consolidados e monta as notas ---
def _gerar_notas_por_periodo(periodo: str) -> dict:
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT resultado_json FROM historico_relatorio_consolidado WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nenhum relatí³rio consolidado encontrado para o perí­odo."}
    
    dados_consolidados = json.loads(row[0]).get("dados", {})
    
    # Navega na estrutura aninhada
    bp_raw = dados_consolidados.get("analise_bp", {})
    bp = bp_raw.get("dados", {}).get("dados", {}) if bp_raw.get("dados") else {}
    if not bp:
        bp = bp_raw.get("dados", {})
    
    orc_raw = dados_consolidados.get("analise_orcamentaria", {})
    orc = orc_raw.get("dados", {}).get("atual", {}) if orc_raw.get("dados") else {}
    
    custo_raw = dados_consolidados.get("custo_pessoal", {})
    custo = custo_raw.get("dados", {}) if custo_raw.get("dados") else {}
    
    bf_raw = dados_consolidados.get("analise_financeira_bf", {})
    bf = bf_raw.get("dados", {}) if bf_raw.get("dados") else {}
    
    dfc_raw = dados_consolidados.get("analise_dfc", {})
    dfc = dfc_raw.get("dados", {}) if dfc_raw.get("dados") else {}
    
    dvp_raw = dados_consolidados.get("analise_patrimonial", {})
    dvp = dvp_raw.get("dados", {}) if dvp_raw.get("dados") else {}
    
    centro_raw = dados_consolidados.get("centro_custos", {})
    centro = centro_raw.get("dados", {}) if centro_raw.get("dados") else {}
    
    liq_raw = dados_consolidados.get("liquidez", {})
    liq = liq_raw.get("dados", {}) if liq_raw.get("dados") else {}
    
    def fmt(v):
        if not v: return "R$ 0,00"
        return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def pct(v):
        if not v: return "0,00%"
        return f"{v:.2f}%".replace(".", ",")
    
    def var(a, b):
        if not b: return "0,00%"
        return f"{((a-b)/b)*100:.2f}%".replace(".", ",")
    
    def vl(chave, tipo="atual"):
        d = bp.get(chave, {})
        return d.get(tipo, 0) if isinstance(d, dict) else 0
    
    notas = []
    
    # Nota 1 - Contexto
    notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
        "texto": "O Conselho Federal de Enfermagem (Cofen) é autarquia federal que integra o Sistema Cofen/Conselhos Regionais. Estas notas acompanham o Relatório Consolidado de Análise Contábil do 3º trimestre de 2026 e compreendem o Balancete de Verificação, o Balanço Financeiro (BF), o Balanço Orçamentário (BO), o Balanço Patrimonial (BP), a Demonstração dos Fluxos de Caixa (DFC), a Demonstração das Mutações do Patrimônio Líquido (DMPL) e a Demonstração das Variações Patrimoniais (DVP).<br><br>As demonstraçíµes foram elaboradas conforme a Lei nº 4.320/1964, a Resolução Cofen nº 340/2008, as Normas Brasileiras de Contabilidade Aplicadas ao Setor Píºblico (NBC TSP), o Manual de Contabilidade Aplicada ao Setor Píºblico (MCASP) e as Resoluçíµes Cofen nº 764/2024, nº 799/2025 e nº 814/2026. Os saldos do perí­odo anterior utilizados para comparação correspondem í  posição de setembro de 2025."})
    
    # Nota 2 - Caixa
    caixa_at = vl("caixa", "atual")
    caixa_an = vl("caixa", "anterior")
    if caixa_at > 0:
        notas.append({"titulo": "NOTA 2 — CAIXA E EQUIVALENTES DE CAIXA",
            "texto": f"O saldo de caixa e equivalentes em 30/09/2026 é de {fmt(caixa_at)}, redução de {var(caixa_at, caixa_an)} frente aos {fmt(caixa_an)} do perí­odo anterior. A variação decorre do fluxo de pagamentos de despesas, com destaque para o grupo de serviços de pessoa jurí­dica. O saldo foi conciliado entre Balancete, BP, BF e DFC.<br><br>A geração lí­quida de caixa no perí­odo foi positiva em R$ 17.076.790,82 (DFC), contra R$ 14.337.040,60 no perí­odo anterior (+19,11%)."})
    
    # Nota 3 - Créditos
    ac_at = vl("ativo_circulante", "atual")
    ac_an = vl("ativo_circulante", "anterior")
    rlp_at = vl("ativo_realizavel", "atual")
    rlp_an = vl("ativo_realizavel", "anterior")
    if ac_at > 0:
        notas.append({"titulo": "NOTA 3 — CRÉDITOS E ATIVO REALIZÁVEL (COTAS-PARTES A RECEBER)",
            "texto": f"O Ativo Circulante totalizou {fmt(ac_at)} ({var(ac_at, ac_an)}), dos quais R$ 112.729.432,69 correspondem a créditos de curto prazo. O Ativo Realizável de longo prazo soma {fmt(rlp_at)}, e o Ativo Não Circulante, R$ 315.111.651,51 (+149,94%).<br><br>Essas variaçíµes decorrem do registro da previsão de receitas de cotas-partes a receber dos Conselhos Regionais. Em 2025, esse registro foi realizado somente em dezembro; por isso, em 30/09/2025 o saldo comparativo era praticamente nulo (R$ 1.004,19 no realizável)."})
    
    # Nota 4 - Imobilizado
    notas.append({"titulo": "NOTA 4 — IMOBILIZADO, INTANGíVEL E INCORPORAÇÃO DE ATIVOS",
        "texto": "O Imobilizado é de R$ 129.453.937,95 (+4,44%) e o Intangí­vel, de R$ 832.266,06. No perí­odo foram incorporados ativos no total de R$ 16.271.957,08, conforme o relatí³rio, assim discriminados:<br><br>â€¢ Outras máquinas, aparelhos e equipamentos: R$ 65.962,97<br>â€¢ Mobiliário em geral: R$ 240.628,83<br>â€¢ Edifí­cio Futura Sede Cofen: R$ 6.682.639,01<br>â€¢ Bens não ativáveis: R$ 21.081,55<br>â€¢ PLATEC — Cofen, investimentos: R$ 9.261.645,32<br><br><i>Observação: a soma aritmética das parcelas acima resulta em R$ 16.271.957,68, diferença de R$ 0,60 em relação ao total informado. A discriminação será revisada antes da divulgação definitiva.</i><br><br>Os estoques somam R$ 185.551,08 (R$ 69.447,74 no perí­odo anterior)."})
    
    # Nota 5 - Passivos
    pc_at = vl("passivo_circulante", "atual")
    pc_an = vl("passivo_circulante", "anterior")
    pnc_at = vl("passivo_nao_circulante", "atual")
    pnc_an = vl("passivo_nao_circulante", "anterior")
    if pc_at > 0:
        notas.append({"titulo": "NOTA 5 — PASSIVO CIRCULANTE E NíƒO CIRCULANTE",
            "texto": f"O Passivo Circulante é de {fmt(pc_at)} ({var(pc_at, pc_an)}), estável. O Passivo Não Circulante é de {fmt(pnc_at)}, redução de {var(pnc_at, pnc_an)} em relação aos {fmt(pnc_an)} anteriores, em razão da quitação do PCCS ao longo de 2025, que em setembro daquele ano ainda estava provisionado. O passivo total é de R$ 12.238.786,04 (—48,28%).<br><br>Os valores restituí­veis (ingressos e dispíªndios extraorçamentários) compreendem retençíµes de tributos, consignaçíµes, cauçíµes e garantias."})
    
    # Nota 6 - PL
    pl_at = vl("patrimonio_liquido", "atual")
    pl_an = vl("patrimonio_liquido", "anterior")
    if pl_at > 0:
        notas.append({"titulo": "NOTA 6 — PATRIMí”NIO LíQUIDO",
            "texto": f"O Patrimí´nio Lí­quido é de {fmt(pl_at)} ({var(pl_at, pl_an)}). Conforme a DMPL, o saldo inicial de R$ 588.096.000,72 foi acrescido do resultado patrimonial do perí­odo de R$ 16.272.243,89, sem outras mutaçíµes. O crescimento frente ao perí­odo anterior reflete principalmente o registro, em dezembro de 2025, das previsíµes de receitas de curto e longo prazo de cotas-partes a receber de anos anteriores."})
    
    # Nota 7 - Orçamento Receita
    rec_at = orc.get("receita_realizada", 0)
    if rec_at > 0:
        notas.append({"titulo": "NOTA 7 — EXECUí‡íƒO ORí‡AMENTíRIA DA RECEITA",
            "texto": f"A receita orçada para 2026 é de R$ 232.000.000,00 (+1,01% sobre 2025) e a receita realizada, de {fmt(rec_at)} (+1,73%), equivalente a 79,58% do orçamento.<br><br>O crescimento modesto da receita recomenda conservadorismo na assunção de novos gastos. As receitas de capital são eventuais; a variação de —85,47% decorre de, em 2025, ter havido a baixa de veí­culo sinistrado e indenizado pela seguradora (R$ 57.487,00)."})
    
    # Nota 8 - Orçamento Despesa
    desp_at = orc.get("despesa_empenhada", 0)
    if desp_at > 0:
        notas.append({"titulo": "NOTA 8 — EXECUí‡íƒO ORí‡AMENTíRIA DA DESPESA E RESTOS A PAGAR",
            "texto": f"A despesa orçada é de R$ 319.721.745,52 (—4,97%) e a despesa empenhada, de {fmt(desp_at)} (+9,80%), com execução de 79,94%. O resultado orçamentário é deficitário em R$ 70.944.403,02, coberto pelo superávit financeiro de exercí­cios anteriores. Os restos a pagar não processados a liquidar somam R$ 17.170.546,09 (—9,20%)."})
    
    # Nota 9 - DFC
    notas.append({"titulo": "NOTA 9 — FLUXOS DE CAIXA",
        "texto": "Pelo método direto, o fluxo operacional lí­quido foi de R$ 33.340.393,59 (—9,38%); o fluxo de investimento foi de —R$ 16.263.602,77; e não houve fluxo de financiamento. A geração lí­quida de caixa foi de R$ 17.076.790,82. A DFC é elaborada pelo regime de caixa, sem considerar empenhos emitidos ou liquidados e não pagos."})
    
    # Nota 10 - DVP
    notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
        "texto": "As Variaçíµes Patrimoniais Aumentativas (VPA) somaram R$ 181.312.304,85 (—3,81%). As Variaçíµes Patrimoniais Diminutivas (VPD) somaram R$ 165.040.060,96 (—10,97%), com destaque para Pessoal e Encargos (R$ 45.949.294,00), Serviços de Terceiros (R$ 65.884.180,07) e Transferíªncias Concedidas (R$ 30.067.473,23). O superávit patrimonial é de R$ 16.272.243,89, com margem patrimonial de 8,97%."})
    
    # Nota 11 - Custo
    pct_custo = custo.get("pct_custo_total", 0)
    if pct_custo > 0:
        notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
            "texto": f"A apuração em 12 meses, nos termos da Resolução Cofen nº 814/2026, resulta em custo de pessoal bruto de R$ 67.338.400,07 sobre Receita Corrente Lí­quida de R$ 226.242.979,74. O custo equivale a {pct(pct_custo)} da RCL, abaixo do limite de 50% (R$ 113.121.489,87), com margem disponí­vel de R$ 45.783.089,80. A entidade está abaixo da faixa de alerta."})
    
    # Nota 12 - Balanço Financeiro (NOVO)
    if bf:
        notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
            "texto": "As receitas orçamentárias de R$ 184.635.554,82 e os recebimentos extraorçamentários de R$ 17.241.359,90, somados ao saldo do exercí­cio anterior de R$ 169.963.364,97, totalizam ingressos de R$ 371.840.279,69, igual ao total de dispíªndios. As despesas orçamentárias pagas foram de R$ 151.902.488,03 (correntes: R$ 135.637.750,95; capital: R$ 16.264.737,08) e os pagamentos extraorçamentários, de R$ 33.052.038,03. Os recebimentos extraorçamentários caí­ram 13,62% e os pagamentos aumentaram 5,45%."})
    
    # Nota 13 - Centro de Custos (NOVO)
    if centro:
        notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
            "texto": "O custo total apropriado aos centros de custo foi de R$ 167.542.179,02 (+0,41%). O maior é AF 05 — Coordenação/Orientação, com R$ 57.933.243,18 (+28,35%), seguido de AF 06 — Despesas Administrativas (R$ 37.055.602,36) e AF 02 — Inscrição, Registro e Cadastro (R$ 24.264.700,14). Os demais centros apresentaram redução entre 5,21% e 15,50%. O crescimento de AF 05 deve ser monitorado quanto í  eficiíªncia alocativa."})
    
    # Nota 14 - índices de Liquidez (NOVO)
    if liq:
        notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
            "texto": "Os í­ndices de liquidez geral e corrente foram influenciados pelo registro das cotas-partes a receber (Nota 3). Os de liquidez estão calculados sobre o passivo circulante de R$ 11.725.635,04.<br><br><table style='width:100%; border-collapse:collapse; margin-top:10px; font-size:11px;'><tr style='background:#003366; color:#fff;'><th style='padding:5px; border:1px solid #ccc;'>Indicador</th><th style='padding:5px; border:1px solid #ccc;'>Atual</th><th style='padding:5px; border:1px solid #ccc;'>Anterior</th></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Liquidez Imediata</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>15,93</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>18,28</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Liquidez Corrente</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>25,71</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>18,47</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Liquidez Seca</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>25,70</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>18,46</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Liquidez Geral</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>39,74</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>9,06</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Endividamento Geral</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>1,98%</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>6,95%</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Part. Capital de Terceiros</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>2,03%</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>7,47%</td></tr><tr><td style='padding:5px; border:1px solid #ccc;'>Imobilização do PL</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>21,42%</td><td style='padding:5px; border:1px solid #ccc; text-align:right;'>39,13%</td></tr></table>"})
    
    # Nota 15 - Integridade (NOVO)
    notas.append({"titulo": "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO",
        "texto": "A matriz de integridade cruzou Balancete, BP, BF, BO, DFC, DVP e DMPL. A conformidade foi confirmada para os grupos patrimoniais, VPA, VPD, receitas correntes, caixa e equivalentes, despesas correntes e de capital pagas e incorporação de ativos.<br><br>Quatro itens apresentaram divergíªncia, decorrentes de estornos de restos a pagar que o sistema contábil (Implanta) não tratou adequadamente; o chamado correspondente foi aberto junto ao fornecedor:<br><br>â€¢ Valores restituí­veis — dispíªndios: R$ 222.353,33<br>â€¢ RP não processados — a liquidar: R$ 134.400,00<br>â€¢ RP não proc. — despesas correntes canceladas: R$ 58.302,51<br>â€¢ RP não processados pagos: R$ 7.220,00<br><br>As diferenças referem-se ao tratamento de estornos de restos a pagar e não afetam o resultado patrimonial nem o saldo de caixa. Ficam pendentes de regularização e serão reavaliadas apí³s resposta do chamado."})
    
    return {"erro": False, "periodo": periodo, "notas": notas}

@app.get("/api/notas_explicativas/{periodo}")
async def api_notas_explicativas(periodo: str):
    return _gerar_notas_por_periodo(periodo)

# --- API: salvar histí³rico ---
@app.post("/salvar_notas_explicativas/{periodo}")
async def salvar_notas_explicativas(periodo: str):
    import sqlite3, json, os
    from datetime import datetime
    dados = _gerar_notas_por_periodo(periodo)
    if dados.get("erro"):
        return {"ok": False, "mensagem": dados.get("mensagem")}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_notas_explicativas (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Notas explicativas salvas com sucesso!"}

# --- API: listar histí³rico ---
@app.get("/historico_notas_explicativas")
async def historico_notas_explicativas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_notas_explicativas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

# --- API: buscar histí³rico por id ---
@app.get("/historico_notas_explicativas/{id}")
async def buscar_notas_explicativas(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_notas_explicativas WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": "não encontrado"}
    return {"periodo": row[0], "data_geracao": row[1], "dados": json.loads(row[2])}

# --- API: excluir histí³rico ---
@app.delete("/excluir_notas_explicativas/{id}")
async def excluir_notas_explicativas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_notas_explicativas WHERE id = ?", (id,))
    cur.execute("DELETE FROM observacoes_notas WHERE relatorio_id = ?", (id,))
    cur.execute("DELETE FROM conclusao_notas WHERE relatorio_id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

# --- Observaçíµes por item ---
@app.get("/api/observacoes_notas/{relatorio_id}")
async def get_observacoes_notas(relatorio_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, item, texto FROM observacoes_notas WHERE relatorio_id = ?", (relatorio_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "item": r[1], "texto": r[2]} for r in rows]

@app.post("/api/observacoes_notas/{relatorio_id}")
async def post_observacao_notas(relatorio_id: int, request: Request):
    import sqlite3, os
    from datetime import datetime
    dados = await request.json()
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO observacoes_notas (relatorio_id, item, texto, data_criacao) VALUES (?, ?, ?, ?)",
                (relatorio_id, dados.get("item", ""), dados.get("texto", ""), datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/observacoes_notas/{obs_id}")
async def del_observacao_notas(obs_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM observacoes_notas WHERE id = ?", (obs_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

# --- Conclusão ---
@app.get("/api/conclusao_notas/{relatorio_id}")
async def get_conclusao_notas(relatorio_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, texto FROM conclusao_notas WHERE relatorio_id = ?", (relatorio_id,))
    row = cur.fetchone()
    conn.close()
    return {"id": row[0], "texto": row[1]} if row else {"id": None, "texto": ""}

@app.post("/api/conclusao_notas/{relatorio_id}")
async def post_conclusao_notas(relatorio_id: int, request: Request):
    import sqlite3, os
    from datetime import datetime
    dados = await request.json()
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM conclusao_notas WHERE relatorio_id = ?", (relatorio_id,))
    cur.execute("INSERT INTO conclusao_notas (relatorio_id, texto, data_criacao) VALUES (?, ?, ?)",
                (relatorio_id, dados.get("texto", ""), datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    conn.commit()
    conn.close()
    return {"ok": True}

# --- PDF ---
@app.get("/api/declaracao_conformidade")
async def listar_itens_declaracao():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, ordem, texto, ativo FROM itens_declaracao_conformidade WHERE ativo = TRUE ORDER BY ordem, id")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "ordem": r[1], "texto": r[2], "ativo": r[3]} for r in rows]

@app.post("/api/declaracao_conformidade")
async def incluir_item_declaracao(request: Request):
    import sqlite3, os
    body = await request.json()
    texto = (body.get("texto") or "").strip()
    if not texto:
        return {"ok": False, "mensagem": "Texto vazio"}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(ordem), 0) + 1 FROM itens_declaracao_conformidade")
    prox_ordem = cur.fetchone()[0]
    cur.execute("INSERT INTO itens_declaracao_conformidade (ordem, texto) VALUES (?, ?)", (prox_ordem, texto))
    novo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"ok": True, "id": novo_id, "ordem": prox_ordem, "texto": texto}

@app.put("/api/declaracao_conformidade/{item_id}")
async def editar_item_declaracao(item_id: int, request: Request):
    import sqlite3, os
    body = await request.json()
    texto = (body.get("texto") or "").strip()
    if not texto:
        return {"ok": False, "mensagem": "Texto vazio"}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE itens_declaracao_conformidade SET texto = ? WHERE id = ?", (texto, item_id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/declaracao_conformidade/{item_id}")
async def excluir_item_declaracao(item_id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM itens_declaracao_conformidade WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/notas_mcasp")
async def api_get_notas_mcasp():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, codigo, nivel, titulo, texto, ordem FROM notas_mcasp_modelo ORDER BY ordem")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/notas_mcasp/salvar")
async def api_salvar_notas_mcasp(request: Request):
    import sqlite3, os
    body = await request.json()
    itens = body.get("itens", [])
    if not itens:
        return {"ok": False, "mensagem": "Nenhum item enviado"}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        for item in itens:
            cur.execute("UPDATE notas_mcasp_modelo SET texto = ? WHERE id = ?", (item["texto"], item["id"]))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()

@app.post("/api/notas_mcasp/gerar_auto")
async def api_gerar_auto_mcasp(request: Request):
    import sqlite3, os, json
    body = await request.json()
    periodo = body.get("periodo", "2026-TRIMESTRE-3")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def brl(v):
        if v is None: return "R$ 0,00"
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # 1. Le Balanco Patrimonial
    cur.execute("SELECT resultado_json FROM historico_analise_bp WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_bp = cur.fetchone()
    bp = json.loads(row_bp[0]).get('dados', {}) if row_bp else {}
    
    # 2. Le Balanco Orcamentario
    cur.execute("SELECT resultado_json FROM historico_analise_orcamentaria WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_bo = cur.fetchone()
    bo = json.loads(row_bo[0]).get('atual', {}) if row_bo else {}
    
    # 3. Le DFC
    cur.execute("SELECT resultado_json FROM historico_analise_dfc WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row_dfc = cur.fetchone()
    dfc = json.loads(row_dfc[0]).get('dados', {}) if row_dfc else {}
    
    # Monta os textos
    t_bp = f"O Ativo Circulante totalizou {brl(bp.get('ativo_circulante', {}).get('atual'))}, sendo composto principalmente por Caixa ({brl(bp.get('caixa', {}).get('atual'))}) e Creditos a Curto Prazo ({brl(bp.get('creditos', {}).get('atual'))}). O Ativo Nao Circulante somou {brl(bp.get('ativo_nao_circulante', {}).get('atual'))}."
    
    t_bo = f"A Receita Realizada no periodo foi de {brl(bo.get('receita_realizada'))}, enquanto a Despesa Empenhada atingiu {brl(bo.get('despesa_empenhada'))}. O Resultado Orcamentario apresentou um {'superavit' if bo.get('superavit', 0) >= 0 else 'deficit'} de {brl(abs(bo.get('superavit', 0)))}."
    
    t_dfc = f"As atividades operacionais geraram um fluxo liquido de caixa positivo de {brl(dfc.get('operacional', {}).get('liquido', {}).get('atual'))}."
    
    textos = {
        "3.1": "As demonstracoes contabeis foram elaboradas com base nos registros oficiais da entidade.",
        "3.1.1": f"Os creditos a curto prazo totalizam {brl(bp.get('creditos', {}).get('atual'))}.",
        "3.1.2": f"O ativo nao circulante (imobilizado e intangivel) totaliza {brl(bp.get('ativo_nao_circulante', {}).get('atual'))}.",
        "3.3.1": t_bo,
        "3.3.3": t_bo,
        "3.5": t_dfc
    }
    
    try:
        for codigo, texto in textos.items():
            cur.execute("UPDATE notas_mcasp_modelo SET texto = ? WHERE codigo = ?", (texto, codigo))
        conn.commit()
        return {"ok": True, "mensagem": "Rascunho gerado com dados reais!"}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()



@app.get("/notas_mcasp_novo")
def rota_notas_mcasp_novo():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "notas_explicativas.html")
    return FileResponse(caminho)

@app.get("/notas_mcasp")
def rota_notas_mcasp():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "notas_mcasp.html")
    return FileResponse(caminho)

@app.get("/gerar_pdf_notas/{id}")
def gerar_pdf_notas(id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, sqlite3, os, json, re

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_notas_explicativas WHERE id = ?", (id,))
    row = cur.fetchone()
    cur.execute("SELECT contador_nome, contador_crc, contador_uf, contador_cpf FROM configuracoes_entidade LIMIT 1")
    row_contador = cur.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, res_json = row
    dados_notas = json.loads(res_json)
    notas = dados_notas.get("notas", [])

    nome_contador = row_contador[0] if row_contador else ""
    crc_bruto = row_contador[1] if row_contador else ""
    uf_contador = row_contador[2] if row_contador else ""
    cpf_bruto = row_contador[3] if row_contador else ""

    crc_limpo = re.sub(r"[^A-Z0-9]", "", crc_bruto.upper())
    if len(crc_limpo) >= 3 and crc_limpo[:2].isalpha():
        numero_crc = crc_limpo[2:]
    else:
        numero_crc = crc_limpo
    crc_formatado = numero_crc + "/" + uf_contador.upper() if uf_contador else numero_crc

    cpf_limpo = re.sub(r"[^0-9]", "", cpf_bruto)
    if len(cpf_limpo) == 11:
        cpf_formatado = "***." + cpf_limpo[3:6] + ".***-**"
    else:
        cpf_formatado = cpf_bruto

    html_notas = ""
    for n in notas:
        html_notas += '<div class="nota"><div class="nota-header"><h3>' + n["titulo"] + '</h3></div><p>' + n["texto"] + '</p></div>'

    # Le itens da declaracao do banco
    conn2 = sqlite3.connect(db_path)
    cur2 = conn2.cursor()
    cur2.execute("SELECT texto FROM itens_declaracao_conformidade WHERE ativo = TRUE ORDER BY ordem, id")
    itens_decl = [r[0] for r in cur2.fetchall()]
    conn2.close()
    html_itens_declaracao = ""
    for i, txt in enumerate(itens_decl, start=1):
        html_itens_declaracao += '<p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>' + str(i) + '.</b> ' + txt + '</p>'

    html_declaracao = (
        '<div style="margin-top: 40px; background: #fff; padding: 30px; border-radius: 8px; border-left: 5px solid #003366; page-break-before: always;">'
        '<h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-top: 0; margin-bottom: 20px; font-size: 15px; text-transform: uppercase;">Declaração de Conformidade</h3>'
        '<p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;">Declaramos, na qualidade de responsáveis pela gestão e pela elaboração das demonstraçíµes contábeis consolidadas do Conselho Federal de Enfermagem (COFEN), referentes ao perí­odo de ' + periodo + ', que:</p>'
        + html_itens_declaracao
        + '<div style="margin-top: 50px; text-align: center;">'
        '<p style="margin: 0; font-size: 14px; font-weight: bold; color: #003366;">' + nome_contador + '</p>'
        '<p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">CRC: ' + crc_formatado + '</p>'
        '<p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">CPF: ' + cpf_formatado + '</p>'
        '</div></div>'
    )

    html_pdf = ('<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
        '<style>'
        'body { font-family: Arial, sans-serif; padding: 20px; color: #333; }'
        '.nota { margin-bottom: 30px; page-break-inside: avoid; }'
        '.nota-header { border-bottom: 1px solid #003366; padding-bottom: 5px; margin-bottom: 10px; }'
        '.nota-header h3 { color: #003366; margin: 0; font-size: 14px; text-transform: uppercase; }'
        '.nota p { text-align: justify; line-height: 1.6; font-size: 12px; margin: 0; color: #444; }'
        '</style></head><body>'
        '<h1 style="color: #003366; text-align: center; margin-bottom: 30px;">Notas Explicativas - ' + periodo + '</h1>'
        + html_notas + html_declaracao + '</body></html>')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_pdf, wait_until="networkidle")
        page.wait_for_timeout(1500)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=notas_explicativas_" + str(id) + ".pdf"})
@app.post("/api/editar_nota/{relatorio_id}/{indice}")
async def editar_nota(relatorio_id: int, indice: int, request: Request):
    import sqlite3, json, os
    dados = await request.json()
    novo_texto = dados.get("texto", "")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT resultado_json FROM historico_notas_explicativas WHERE id = ?", (relatorio_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"ok": False, "mensagem": "Histí³rico não encontrado."}
    
    dados_notas = json.loads(row[0])
    notas = dados_notas.get("notas", [])
    if indice < 0 or indice >= len(notas):
        conn.close()
        return {"ok": False, "mensagem": "índice inválido."}
    
    notas[indice]["texto"] = novo_texto
    dados_notas["notas"] = notas
    cur.execute("UPDATE historico_notas_explicativas SET resultado_json = ? WHERE id = ?",
                (json.dumps(dados_notas, ensure_ascii=False), relatorio_id))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.post("/api/incluir_nota/{relatorio_id}")
async def incluir_nota(relatorio_id: int, request: Request):
    import sqlite3, json, os
    dados = await request.json()
    titulo = dados.get("titulo", "")
    texto = dados.get("texto", "")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT resultado_json FROM historico_notas_explicativas WHERE id = ?", (relatorio_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"ok": False, "mensagem": "Histí³rico não encontrado."}
    
    dados_notas = json.loads(row[0])
    notas = dados_notas.get("notas", [])
    notas.append({"titulo": titulo, "texto": texto})
    dados_notas["notas"] = notas
    
    cur.execute("UPDATE historico_notas_explicativas SET resultado_json = ? WHERE id = ?",
                (json.dumps(dados_notas, ensure_ascii=False), relatorio_id))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.delete("/api/excluir_nota/{relatorio_id}/{indice}")
async def excluir_nota(relatorio_id: int, indice: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT resultado_json FROM historico_notas_explicativas WHERE id = ?", (relatorio_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"ok": False, "mensagem": "Histí³rico não encontrado."}
    
    dados_notas = json.loads(row[0])
    notas = dados_notas.get("notas", [])
    if indice < 0 or indice >= len(notas):
        conn.close()
        return {"ok": False, "mensagem": "índice inválido."}
    
    notas.pop(indice)
    dados_notas["notas"] = notas
    
    cur.execute("UPDATE historico_notas_explicativas SET resultado_json = ? WHERE id = ?",
                (json.dumps(dados_notas, ensure_ascii=False), relatorio_id))
    conn.commit()
    conn.close()
    return {"ok": True}
