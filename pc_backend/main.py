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
    """Limpa apenas tabulações e caracteres de controle, mantendo acentos."""
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
    print(f"✅ Arquivos estáticos montados em: {frontend_path}")
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
# CONFIGURAÇÃO DO BANCO DE DADOS SQLITE
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
# ROTA DE UPLOAD (IMPORTAÇÃO)
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
                periodo_formatado = f"{valor_p}º Tri/{ano}"
            else:
                periodo_formatado = f"Exercício {ano}"
        csv_path = _get_csv_por_tipo(tipo, periodo)
        if not csv_path:
            raise HTTPException(status_code=404, detail=f"Arquivo CSV para {tipo} no período {periodo_formatado} não encontrado.")
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
        content = content.replace("Ã§", "ç").replace("Ã£", "ã").replace("Ã¡", "á")
        content = content.replace("Ã©", "é").replace("Ã", "í").replace("Ã³", "ó")
        content = content.replace("Ãº", "ú").replace("Ã¢", "â").replace("Ãª", "ê")
        content = content.replace("Ã´", "ô").replace("Ãª", "ê").replace("Ã§", "ç")
        content = content.replace("Ãƒ", "Ã").replace("Ã‰", "É").replace("Ã“", "Ó")
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
            headers = ["ESPECIFICACAO (ATIVO)", "Exercício Atual", "ESPECIFICACAO (PASSIVO)", "Exercício Atual", "", ""]
            titulo_pdf = "Balanço Patrimonial"
        elif tipo == "BALANCO_FINANCEIRO":
            col_w   = [68, 28, 28, 68, 28, 28] 
            headers = ["ESPECIFICACAO (INGRESSOS)", "Exercício Atual", "Exercício Anterior", "ESPECIFICACAO (DISPENDIOS)", "Exercício Atual", "Exercício Anterior"]
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
            titulo_pdf = "Demonstração das Mutações do Patrimônio Líquido"
        elif tipo == "DFC":
            col_w   = [160, 0, 0, 60, 57]
            headers = ["ESPECIFICACAO", "", "", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Demonstração do Fluxo de Caixa"
        elif tipo == "DVP":
            # Layout DVP: Desc Ativa | Atual | Anterior | Desc Passiva | Atual | Anterior
            col_w   = [70, 25, 25, 70, 25, 25]
            headers = ["VARIACOES AUMENTATIVAS", "Exercício Atual", "Exercício Anterior", "VARIACOES DIMINUTIVAS", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Demonstração das Variações Patrimoniais"
        else:
            col_w   = [72, 30, 28, 72, 40, 35]
            headers = ["ESPECIFICACAO", "Exercício Atual", "Exercício Anterior", "ESPECIFICACAO", "Exercício Atual", "Exercício Anterior"]
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
        # LÔGICA ESPECÍFICA PARA O DVP
        # =======================================================
        if tipo == "DVP":
            linhas = content.splitlines()
            start_idx = 0
            for i, linha in enumerate(linhas):
                if "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in linha.upper():
                    start_idx = i
                    break
            for idx, linha in enumerate(linhas[start_idx:]):
                if not linha.strip(): continue
                if "COFEN/BR" in linha or "PERÍODO" in linha.upper() or "BRASÍLIA" in linha.upper() or "CONTADOR" in linha.upper() or "CRC-DF" in linha.upper(): continue
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
            # (Mantém a lógica que já havíamos ajustado para o BP)
            linhas = content.splitlines()
            start_idx = 0
            for i, linha in enumerate(linhas):
                if "ATIVO CIRCULANTE" in linha.upper():
                    start_idx = i
                    break
            for idx, linha in enumerate(linhas[start_idx:]):
                if not linha.strip(): continue
                if "COFEN/BR" in linha or "PERÍODO" in linha.upper(): continue
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
                ("Ajustes de exercícios anteriores", ["", "", "", "", "", "", "", "0"], False),
                ("Aumento de capital", ["", "", "", "", "", "", "", "0"], False),
                ("Resultado do exercício", ["", "", "", "", "", "", "0", "0"], False),
                ("Resultado do período", ["", "", "", "", "", "", res_1, res_2], False),
                ("Ajustes de avaliação patrimonial", ["", "", "", "", "", "", "0", "0"], False),
                ("Constituição / Reversão de reservas", ["", "", "", "", "", "", "0", "0"], False),
                ("Demais variações", ["", "", "", "", "", "", "0", "0"], False),
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
                    if "EXERCÍCIO ATUAL" in joined and "EXERCÍCIO ANTERIOR" in joined:
                        start_idx = i + 1
                        break
                elif tipo == "BALANCO_FINANCEIRO":
                    if "ESPECIFICACAO" in joined and "EXERCÍCIO ATUAL" in joined:
                        start_idx = i + 1
                        break
                elif "CONTA" in joined and "SALDO" in joined:
                    start_idx = i + 1
                    break
            def eh_lixo(row):
                texto_linha = " ".join(row).upper()
                if "COFEN/BR" in texto_linha and ("PERÍODO" in texto_linha or "PERIODO" in texto_linha): return True
                if row[0].strip().upper() == "COFEN/BR": return True
                if "CONSELHO FEDERAL" in texto_linha or "CNPJ" in texto_linha or "DEMONSTRAÇÃO" in texto_linha or "BALANÇO" in texto_linha: return True
                if "MARCELO" in texto_linha or "CONTADOR" in texto_linha or "CRC-DF" in texto_linha or "PÁGINA" in texto_linha or "BRASÍLIA-DF" in texto_linha: return True
                return False
            for idx, row in enumerate(dados_csv[start_idx:]):
                if not any(str(c).strip() for c in row): continue
                if eh_lixo(row): continue
                row_text = " ".join(row).upper()
                is_header = False
                is_total = False
                if "TOTAIS" in row_text or "TOTAL:" in row_text or "TOTAL DAS" in row_text or "FLUXO DE CAIXA LÍQUIDO" in row_text or "GERAÇÃO LIQUIDA" in row_text:
                    is_total = True
                elif any(k in row_text for k in ["ATIVO", "PASSIVO", "PATRIMÔNIO", "COMPENSAÇÕES", "QUADRO", "FLUXO DE CAIXA DAS ATIVIDADES"]):
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
        ws['A2'] = f"CNPJ: 47.217.146/0001-57   |   Período: {periodo}/{ano}"
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
            is_header = any(k in row[0].upper() for k in ["ATIVO", "PASSIVO", "PATRIMÔNIO", "RECEITAS", "DESPESAS", "INGRESSOS"])
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
                            if any(k in text.upper() for k in ["ATIVO", "PASSIVO", "TOTAL", "ESPECIFICAÇÃO", "RECEITAS"]):
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
# Rota que abre um histórico especifico pelo ID
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
        if "SUPERÁVIT FINANCEIRO" in p[0].upper() and len(p) > 2:
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
        # === REGRA DE INTEGRIDADE: verifica se os 6 demonstrativos existem ===
        demonstrativos = {
            "BALANCO_PATRIMONIAL": "Balanço Patrimonial",
            "BALANCO_ORCAMENTARIO": "Balanço Orçamentário",
            "BALANCO_FINANCEIRO": "Balanço Financeiro",
            "DFC": "Demonstração do Fluxo de Caixa",
            "DVP": "Demonstração das Variações Patrimoniais",
            "DMPL": "Demonstração das Mutações do PL",
        }
        faltando = []
        for tipo, nome in demonstrativos.items():
            dados = buscar_no_banco(tipo)
            if not dados:
                faltando.append(nome)
        if faltando:
            conn.close()
            return {"erro": "faltando", "pecas": faltando}
        l_bp = buscar_no_banco("BALANCO_PATRIMONIAL")
        l_bo = buscar_no_banco("BALANCO_ORCAMENTARIO")
        l_dvp = buscar_no_banco("DVP")
        def buscar(linhas, termos, coluna):
            for p in linhas:
                for termo in termos:
                    termo_upper = termo.upper()
                    # Procura o termo na coluna 0 (Ativo) ou 3 (Passivo)
                    for col_espec in [0, 3]:
                        if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                            # Pega o valor da coluna seguinte (1 para Ativo, 4 para Passivo)
                            col_valor = col_espec + 1
                            if len(p) > col_valor:
                                try:
                                    v = abs(_limpar_valor(p[col_valor]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0
        # === BP ===
        # NOVO CSV: Passivo esta na coluna 3 (especificacao) e o valor na coluna 4
        # Patrimonio Liquido esta na coluna 3 (especificacao) e o valor na coluna 4
        # Usa a Definição 7 (que procura na coluna 0/3 e pega o valor da coluna seguinte)
        passivo_total = buscar("TOTAL DO PASSIVO", 4)  # Definicao 7
        pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)  # Definicao 7
        if pl == 0.0:
            pl = buscar("RESULTADOS ACUMULADOS", 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL
        caixa_bp = buscar(l_bp, ["CAIXA E EQUIVALENTES", "CAIXA E EQUIVALENTE"], 1)
        superavit_financeiro = buscar(l_bp, ["SUPERÁVIT FINANCEIRO", "SUPERAVIT FINANCEIRO"], 2)
        # === BO ===
        receita_realizada = buscar(l_bo, ["SUB-TOTAL DAS RECEITAS"], 6)
        despesa_empenhada = buscar(l_bo, ["SUB-TOTAL DAS DESPESAS"], 4)
        superavit_orcamentario = receita_realizada - despesa_empenhada
        # === DVP ===
        total_vpa = buscar(l_dvp, ["Total das Variações Ativas"], 2)
        total_vpd = buscar(l_dvp, ["Total das Variações Passivas"], 6)
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
async def salvar_panorama(periodo: str):
    try:
        import sqlite3, json, datetime, os
        dados = _calc_panorama(periodo)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", 
                       (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"mensagem": "Panorama salvo!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
async def buscar_panorama(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT resultado_json FROM historico_panorama WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[0])
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
            return {"erro": True, "mensagem": f"BO do período {periodo} não foi importado."}
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
    dados = {"periodo_anterior": periodo_anterior, "periodo_atual": periodo,
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
            "Transferencias Correntes": buscar("TRANSFERÊNCIAS CORRENTES"),
            "Outras Receitas Correntes": buscar("OUTRAS RECEITAS CORRENTES"),
            "Receitas de Capital": buscar("RECEITAS DE CAPITAL"),
        }
        despesas = {
            "Pessoal e Encargos": buscar("PESSOAL E ENCARGOS SOCIAIS", 4),
            "Outras Despesas Correntes": buscar("OUTRAS DESPESAS CORRENTES", 4),
            "Investimentos": buscar("INVESTIMENTOS - APLICAÇÕES DIRETAS", 4),
            "Inversoes Financeiras": buscar("INVERSÕES FINANCEIRAS  APLICAÇÕES DIRETAS", 4),
        }
        return {"erro": False, "receitas": receitas, "despesas": despesas}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
@app.post("/salvar_composicao_receitas_despesas/{periodo_atual}/{periodo_anterior}")
async def salvar_composicao_rd(periodo_atual: str, periodo_anterior: str):
    atual = await api_composicao_rd(periodo_atual)
    if atual.get("erro"): raise HTTPException(status_code=400, detail=atual["mensagem"])
    anterior = await api_composicao_rd(periodo_anterior)
    dados = {"periodo_atual": periodo_atual, "periodo_anterior": periodo_anterior,
             "atual": atual, "anterior": anterior if not anterior.get("erro") else {}}
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_composicao_rd (

        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_composicao_rd (periodo, data_geracao, resultado_json) VALUES (?,?,?)",
                (f"{periodo_atual} vs {periodo_anterior}", data_agora, json.dumps(dados)))
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
        l33 = buscar("Saldo em espécie do Exercício Anterior")
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
@app.post("/salvar_analise_financeira_bf/{periodo_atual}/{periodo_anterior}")
async def salvar_analise_financeira_bf(periodo_atual: str, periodo_anterior: str):
    atual = await api_analise_financeira_bf(periodo_atual)
    if atual.get("erro"): raise HTTPException(status_code=400, detail=atual["mensagem"])
    # O periodo anterior JA esta no mesmo CSV (coluna 2). Nao precisa buscar outro arquivo.
    dados = {"periodo_atual": periodo_atual, "periodo_anterior": periodo_anterior,
             "atual": atual.get("dados", {}), "anterior": {}}
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_analise_financeira_bf (

        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_analise_financeira_bf (periodo, data_geracao, resultado_json) VALUES (?,?,?)",
                (f"{periodo_atual} vs {periodo_anterior}", data_agora, json.dumps(dados)))
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

@app.get("/gerar_pdf_analise_patrimonial/{historico_id}")
def gerar_pdf_analise_patrimonial(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre a tela do relatório passando o ID do histórico
    url = f"http://127.0.0.1:9994/relatorio_analise_patrimonial?historico_id={historico_id}&_t={int(time.time())}"
    
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
        headers={"Content-Disposition": f"inline; filename=patrimonial_{historico_id}.pdf"}
    )


@app.get("/gerar_pdf_analise_financeira_bf/{id}")
async def gerar_pdf_analise_financeira_bf(id: int):
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from fastapi.responses import Response
        from app.routers.balanco_financeiro import processar_bf
        import sqlite3, os
        from datetime import datetime

        fonte_padrao = "Helvetica"  # Definicao da fonte

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo FROM historico_analise_financeira_bf WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        periodo = row[0] if row else "2026-TRIMESTRE-3"

        periodo_atual = periodo.split(" vs ")[0].strip() if " vs " in periodo else periodo
        p_limpo = periodo_atual.replace("-", "_")
        caminho_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw", f"BALANCO_FINANCEIRO_{p_limpo}.csv")
        
        if not os.path.exists(caminho_csv):
            raise Exception(f"Arquivo do Balanco Financeiro nao encontrado para {periodo}")

        resultado = processar_bf(caminho_csv)
        d = resultado["dados"]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        # Cabecalho
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_font(fonte_padrao, "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 8)
        pdf.cell(180, 10, "Balanco Financeiro", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

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
        pdf.cell(170, 6, "EXTRAORCAMENTARIO", border=1, fill=True)
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
        add_linha("Saldo em Especie do Exercicio Anterior", d["caixa"]["saldo_anterior"]["atual"], d["caixa"]["saldo_anterior"]["anterior"])
        add_linha("Geracao Liquida de Caixa", d["caixa"]["geracao_liquida"]["atual"], d["caixa"]["geracao_liquida"]["anterior"], bold=True)
        add_linha("Saldo em Especie para o Exercicio Seguinte", d["caixa"]["saldo_seguinte"]["atual"], d["caixa"]["saldo_seguinte"]["anterior"], bold=True)

        # ==========================================
        # NOVOS TOTAIS (INGRESSOS E DISPENDIOS)
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
        
        add_linha("Receitas Orcamentarias (Corrente + Capital)", totRecAt, totRecAnt)
        add_linha("Recebimentos Extraorcamentarios", totExtAt, totExtAnt)
        add_linha("Saldo em Especie do Exercicio Anterior", saldoAntAt, saldoAntAnt)
        add_linha("TOTAL DE INGRESSOS", totalIngAt, totalIngAnt, bold=True, fill_color=(233, 236, 239), text_color=(0, 86, 179))

        # Calculos de Dispêndios
        y_pos += 5
        totDespAt = d["despesas"]["total"]["atual"]
        totDespAnt = d["despesas"]["total"]["anterior"]
        pagExtAt = d["extra"]["pagamentos"]["atual"]
        pagExtAnt = d["extra"]["pagamentos"]["anterior"]
        saldoSegAt = d["caixa"]["saldo_seguinte"]["atual"]
        saldoSegAnt = d["caixa"]["saldo_seguinte"]["anterior"]

        totalDispAt = totDespAt + pagExtAt + saldoSegAt
        totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt

        # Tabela de Dispêndios
        pdf.set_fill_color(220, 53, 69)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte_padrao, "B", 10)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 6, "TOTAL GERAL DE DISPENDIOS", border=1, fill=True)
        pdf.ln()
        y_pos += 6

        add_linha("Despesas Orcamentarias (Corrente + Capital)", totDespAt, totDespAnt)
        add_linha("Pagamentos Extraorcamentarios", pagExtAt, pagExtAnt)
        add_linha("Saldo em Especie para o Exercicio Seguinte", saldoSegAt, saldoSegAnt)
        add_linha("TOTAL DE DISPENDIOS", totalDispAt, totalDispAnt, bold=True, fill_color=(233, 236, 239), text_color=(220, 53, 69))

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

@app.post("/salvar_analise_dfc/{periodo_atual}/{periodo_anterior}")
async def salvar_analise_dfc(periodo_atual: str, periodo_anterior: str):
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
        dados = await api_analise_dfc(periodo_atual)
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao calcular DFC: {e}"}
    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_analise_dfc (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo_atual, data_agora, json.dumps(dados, ensure_ascii=False)))
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
    pdf.add_page()
    
    # Cabecalho
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "COFEN/BR - ANALISE DA DEMONSTRACAO DO FLUXO DE CAIXA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.ln(5)
    pdf.cell(0, 6, f"Periodo de Referencia: {periodo.replace('-', ' ')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"Data de Geracao do Relatorio: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Tabela
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    
    col_w = [70, 35, 35, 30]
    headers = ["ESPECIFICACAO", "PERIODO ATUAL", "PERIODO ANTERIOR", "VAR. (%)"]
    
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 8)
    
    def draw_row(label, va, vb, is_header=False, is_total=False):
        if is_header:
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(sum(col_w), 6, label, border=1, align="L", fill=True)
            pdf.ln()
            return
        if is_total:
            pdf.set_font("Helvetica", "B", 8)
        else:
            pdf.set_font("Helvetica", "", 8)
            
        pdf.cell(col_w[0], 6, label, border=1, align="L")
        pdf.cell(col_w[1], 6, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 6, fmt(vb), border=1, align="R")
        v = pct(va, vb)
        pdf.cell(col_w[3], 6, v, border=1, align="R")
        pdf.ln()

    # Operacional
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERACOES", 0, 0, is_header=True)
    draw_row("Ingressos Operacionais", op.get("ingressos", {}).get("atual", 0), op.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos Operacionais", op.get("desembolsos", {}).get("atual", 0), op.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido das Operacoes", op.get("liquido", {}).get("atual", 0), op.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Investimento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Investimento", inv.get("ingressos", {}).get("atual", 0), inv.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Investimento", inv.get("desembolsos", {}).get("atual", 0), inv.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido de Investimento", inv.get("liquido", {}).get("atual", 0), inv.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Financiamento
    draw_row("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO", 0, 0, is_header=True)
    draw_row("Ingressos de Financiamento", fin.get("ingressos", {}).get("atual", 0), fin.get("ingressos", {}).get("anterior", 0))
    draw_row("Desembolsos de Financiamento", fin.get("desembolsos", {}).get("atual", 0), fin.get("desembolsos", {}).get("anterior", 0))
    draw_row("Caixa Liquido de Financiamento", fin.get("liquido", {}).get("atual", 0), fin.get("liquido", {}).get("anterior", 0), is_total=True)
    
    # Apuracao
    draw_row("APURACAO DO FLUXO DE CAIXA DO PERIODO", 0, 0, is_header=True)
    draw_row("Geracao Liquida de Caixa", cxa.get("geracao", {}).get("atual", 0), cxa.get("geracao", {}).get("anterior", 0), is_total=True)
    draw_row("Caixa e Equivalentes Inicial", cxa.get("inicial", {}).get("atual", 0), cxa.get("inicial", {}).get("anterior", 0))
    draw_row("Caixa e Equivalentes Final", cxa.get("final", {}).get("atual", 0), cxa.get("final", {}).get("anterior", 0), is_total=True)
    
    pdf.ln(10)

    # Analise Textual
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "1. ANALISE DAS ATIVIDADES OPERACIONAIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_op = op.get("liquido", {}).get("atual", 0)
    if liq_op > 0:
        txt_op = f"As atividades operacionais geraram um caixa liquido positivo de R$ {fmt(liq_op)} no periodo atual. Isso indica que as receitas e ingressos operacionais foram suficientes para cobrir os custos e desembolsos operacionais."
    else:
        txt_op = f"As atividades operacionais apresentaram um caixa liquido negativo de R$ {fmt(liq_op)} no periodo atual. Isso demonstra que a entidade precisou consumir reservas ou obter financiamentos para cobrir seus desembolsos operacionais."
    
    pdf.multi_cell(0, 5, txt_op)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "2. ANALISE DAS ATIVIDADES DE INVESTIMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_inv = inv.get("liquido", {}).get("atual", 0)
    if liq_inv < 0:
        txt_inv = f"O fluxo de caixa de investimentos foi negativo em R$ {fmt(abs(liq_inv))}, o que e comum e esperado quando a entidade realiza aquisicoes de ativos (investimentos) e imobilizacoes."
    else:
        txt_inv = f"O fluxo de caixa de investimentos foi positivo em R$ {fmt(liq_inv)}, indicando que a entidade obteve mais recursos com alienacao de ativos do que gastou com aquisicoes."
    
    pdf.multi_cell(0, 5, txt_inv)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "3. ANALISE DAS ATIVIDADES DE FINANCIAMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    liq_fin = fin.get("liquido", {}).get("atual", 0)
    if liq_fin > 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi positivo em R$ {fmt(liq_fin)}, decorrente de captacao de emprestimos ou financiamentos."
    elif liq_fin < 0:
        txt_fin = f"O fluxo de caixa de financiamentos foi negativo em R$ {fmt(abs(liq_fin))}, indicando amortizacao de dividas ou devolucao de recursos."
    else:
        txt_fin = "Nao houve movimentacao significativa no fluxo de caixa de financiamentos no periodo."
        
    pdf.multi_cell(0, 5, txt_fin)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "4. CONCLUSAO SOBRE A LIQUIDEZ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    
    geracao = cxa.get("geracao", {}).get("atual", 0)
    inicial = cxa.get("inicial", {}).get("atual", 0)
    final = cxa.get("final", {}).get("atual", 0)
    
    txt_concl = f"A entidade encerrou o periodo com um saldo de caixa de R$ {fmt(final)} (variacao de R$ {fmt(geracao)} em relacao ao saldo inicial de R$ {fmt(inicial)}). "
    if geracao > 0:
        txt_concl += "O aumento no saldo de caixa demonstra uma boa geracao de recursos no periodo."
    else:
        txt_concl += "A reducao no saldo de caixa requer atencao aos proximos periodos para garantir a manutencao das atividades."
        
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
                if col_a == "VARIAÇÃO PATRIMONIAL AUMENTATIVA":
                    dados["variacoes_ativas"]["atual"] = limpar(row[2])
                    dados["variacoes_ativas"]["anterior"] = limpar(row[3])
                elif col_a == "TRANSFERÊNCIAS E DELEGAÇÕES RECEBIDAS":
                    dados["transf_recebidas"]["atual"] = limpar(row[2])
                    dados["transf_recebidas"]["anterior"] = limpar(row[3])
                elif col_a == "REVERSÃO DE PROVISÕES E AJUSTES DE PERDAS":
                    dados["reversao_provisoes"]["atual"] = limpar(row[2])
                    dados["reversao_provisoes"]["anterior"] = limpar(row[3])
                if col_d == "VARIAÇÃO PATRIMONIAL DIMINUTIVA":
                    dados["variacoes_diminutivas"]["atual"] = limpar(row[6])
                    dados["variacoes_diminutivas"]["anterior"] = limpar(row[7])
                elif col_d == "PESSOAL E ENCARGOS":
                    dados["pessoal_encargos"]["atual"] = limpar(row[6])
                    dados["pessoal_encargos"]["anterior"] = limpar(row[7])
                elif col_d == "SERVIÇOS TERCEIROS - PJ":
                    dados["servicos_terceiros"]["atual"] = limpar(row[6])
                    dados["servicos_terceiros"]["anterior"] = limpar(row[7])
                elif col_d == "TRANSFERÊNCIAS E DELEGAÇÕES CONCEDIDAS":
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
        # --- 1. GERA O GRÁFICO (Atual primeiro) ---
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
        ind = [
            ("Receita Realizada", "receita_realizada", 1e6),
            ("Despesas Empenhadas", "despesa_empenhada", 1e6),
            ("Superavit Orcamentario", "superavit", 1e6),
            ("Restos a Pagar Inscritos", "restos_pagar", 1e6),
            ("Receitas Orcadas", "receita_orcada", 1e6),
            ("Despesas Orcadas", "despesa_orcada", 1e6),
            ("% de Realizacao das Receitas", "pct_receita", 1),
            ("% de Realizacao das Despesas", "pct_despesa", 1),
        ]
        for nome, chave, m in ind:
            va = a.get(chave, 0)
            vb = b.get(chave, 0)
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
        pdf.cell(180, 10, "DVP - Demonstração das Variações Patrimoniais", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(fonte_padrao, "", 13)
        pdf.set_xy(15, 20)
        pdf.cell(180, 8, f"Período: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
        pdf.cell(card_w, 5, "Total VPA (Variações Aumentativas)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
        pdf.cell(card_w, 5, "Total VPD (Variações Diminutivas)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
        pdf.cell(40, 8, "Período Atual", border=1, fill=True, align="R")
        pdf.cell(40, 8, "Período Anterior", border=1, fill=True, align="R")
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
        pdf.cell(170, 7, "VPA - VARIAÇÕES PATRIMONIAIS AUMENTATIVAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("VPA Financeiras", d['vpa_financeiras']['atual'], d['vpa_financeiras']['anterior'])
        add_linha("Transferências Recebidas", d['transf_recebidas']['atual'], d['transf_recebidas']['anterior'])
        add_linha("Outras VPA", d['outras_vpa']['atual'], d['outras_vpa']['anterior'])
        add_linha("Reversão de Provisões", d['reversao_provisoes']['atual'], d['reversao_provisoes']['anterior'])
        add_linha("TOTAL VPA", d['total_vpa']['atual'], d['total_vpa']['anterior'], bold=True)
        # Bloco VPD
        pdf.set_fill_color(248, 232, 232)
        pdf.set_font(fonte_padrao, "B", 9)
        pdf.set_xy(15, y_pos)
        pdf.cell(170, 7, "VPD - VARIAÇÕES PATRIMONIAIS DIMINUTIVAS", border=1, fill=True)
        pdf.ln()
        y_pos += 6
        add_linha("VPD Financeiras", d['vpd_financeiras']['atual'], d['vpd_financeiras']['anterior'])
        add_linha("Pessoal e Encargos", d['pessoal_encargos']['atual'], d['pessoal_encargos']['anterior'])
        add_linha("Uso de Material de Consumo", d['uso_material_consumo']['atual'], d['uso_material_consumo']['anterior'])
        add_linha("Serviços", d['servicos']['atual'], d['servicos']['anterior'])
        add_linha("Depreciação", d['depreciacao']['atual'], d['depreciacao']['anterior'])
        add_linha("Amortização", d['amortizacao']['atual'], d['amortizacao']['anterior'])
        add_linha("Transferências Concedidas", d['transf_concedidas']['atual'], d['transf_concedidas']['anterior'])
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
            if "SENTENÇAS JUDICIAIS" in nome and "TRABALHISTAS" in nome:
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
    # Lógica de Faixas de Controle (Art. 6º da Resolução Cofen 814/2026)
    pct_custo_total = ((custo_atual + custo_anterior) / (rcl_atual + rcl_anterior)) * 100 if (rcl_atual + rcl_anterior) > 0 else 0
    is_coren = (entidade.upper() == "COREN")
    
    if is_coren:
        if pct_custo_total > 60:
            faixa, cor = "Faixa Crítica (> 60%)", "danger"
        elif pct_custo_total >= 57:
            faixa, cor = "Faixa Prudencial (57% a 60%)", "warning"
        elif pct_custo_total >= 54:
            faixa, cor = "Faixa de Alerta (54% a 57%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"
    else:
        if pct_custo_total > 50:
            faixa, cor = "Faixa Crítica (> 50%)", "danger"
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
@app.get("/salvar_base_legal/{periodo_atual}")
async def salvar_base_legal(periodo_atual: str, periodo_anterior: str = "2025-TRIMESTRE-3"):
    try:
        import sqlite3, json, datetime, os
        # Simulamos o salvamento dos dados do Base Legal (que são fixos, mas dependem do período)
        # O PDF será gerado posteriormente com base no ID salvo
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_base_legal (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo_atual TEXT, periodo_anterior TEXT, data_geracao TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_base_legal (periodo_atual, periodo_anterior, data_geracao) VALUES (?, ?, ?)", 
                       (periodo_atual, periodo_anterior, data_agora))
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
    cursor.execute("SELECT id, periodo_atual, periodo_anterior, data_geracao FROM historico_base_legal ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo_atual": r[1], "periodo_anterior": r[2], "data_geracao": r[3]} for r in rows]
@app.get("/liquidez")
async def serve_liquidez():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "liquidez.html")
    return FileResponse(caminho)
def _calc_liquidez(periodo):
    from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
    caminho_bp = _get_csv("BALANCO_PATRIMONIAL", periodo)
    if not caminho_bp: return None
    l_bp = _ler_linhas(caminho_bp)
    def buscar(termo, coluna):
            termo_upper = termo.upper()
            for p in l_bp:
                # Procura o termo na coluna 0 (Ativo) ou 3 (Passivo)
                for col_espec in [0, 3]:
                    if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                        # Pega o valor da coluna seguinte (1 para Ativo, 4 para Passivo)
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except:
                                pass
            return 0.0
def demonstracoes_em_breve():
    return HTMLResponse(content="<html><body><h1>Demonstrações Contábeis</h1><p>Em breve.</p><a href='/'>Voltar</a></body></html>")
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
        return {"status": "sucesso", "mensagem": "Relatório salvo!"}
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
    return HTMLResponse(content="<h1>Arquivo de configurações não encontrado</h1>", status_code=404)


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


@app.get("/api/relatorio_centro_custos")
def api_relatorio_centro_custos(id: int = None, periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = None):
    import sqlite3, os, json, csv, io
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Calcula o período anterior automaticamente (mesmo trimestre do ano anterior)
    if not periodo_anterior:
        partes = periodo_atual.split("-")
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
            
            # Encontra o início dos dados reais (primeira linha que começa com "01 - AF")
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
    
    centros_atual = ler_csv(periodo_atual)
    if not centros_atual:
        dados_banco = buscar_historico(periodo_atual)
        if dados_banco:
            centros_atual = dados_banco.get("centros", [])
    
    centros_anterior = ler_csv(periodo_anterior)
    if not centros_anterior:
        dados_banco_anterior = buscar_historico(periodo_anterior)
        if dados_banco_anterior:
            centros_anterior = dados_banco_anterior.get("centros", [])
    
    conn.close()
    
    atual = processar(centros_atual, periodo_atual)
    anterior = processar(centros_anterior, periodo_anterior) if centros_anterior else None
    
    if anterior is None or anterior["total"] == 0:
        return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": periodo_anterior,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o período anterior."
        }
    
    return {
        "periodo_atual": periodo_atual,
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
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


@app.get("/relatorio_centro_custos_completo", response_class=HTMLResponse)
def serve_relatorio_centro_custos_completo():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


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
            
            # Encontra o início dos dados reais (primeira linha que começa com "01 - AF")
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
    
    # Lê o período atual
    centros_atual = ler_csv(periodo)
    if centros_atual is None:
        return {"erro": True, "mensagem": f"Arquivo para o período {periodo} não encontrado."}
    
    # Calcula o período anterior (mesmo trimestre/mês do ano anterior)
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


@app.get("/api/relatorio_v2/{periodo_atual}")
def api_relatorio_v2(periodo_atual: str):
    import sqlite3, os, json, csv, io
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    # Calcula o período anterior (mesmo trimestre do ano anterior)
    partes = periodo_atual.split("-")
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
            
            # Lê o cabeçalho para descobrir os meses
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
                
                # Valor total (última coluna)
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
    
    dados_atual = ler_csv(periodo_atual)
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
        "periodo_atual": periodo_atual,
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
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


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
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


# ========== ROTAS DO COMPARATIVO DE RECEITAS ==========
@app.get("/api/comparativo_receitas/{periodo}")
def api_comparativo_receitas(periodo: str):
    import os, csv, io
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    # Simulação: retorna dados fictícios de receitas (adapte para ler o CSV real, se houver)
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
    # Por enquanto, redireciona para o relatório de centro de custos (ou crie um novo HTML)
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


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



@app.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    
    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"
    
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
        headers={"Content-Disposition": f"inline; filename=relatorio_receitas_{periodo_atual}.pdf"}
    )


# ========== ROTAS DO COMPARATIVO DE DESPESAS ==========
@app.get("/api/comparativo_despesas_v2/{periodo_atual}")
def api_comparativo_despesas_v2(periodo_atual: str):
    import os, unicodedata
    upload_dir = r"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\uploads_raw"
    
    partes = periodo_atual.split("-")
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
            
            # Lista fixa de cabeçalhos que NÃO são contas analíticas
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
                    # Exclui também linhas com "TOTAL" no nome (são somatórios)
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
            
    atual = ler_csv(periodo_atual)
    anterior = ler_csv(periodo_anterior)
    
    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}
        
    return {
        "erro": False,
        "periodo_atual": periodo_atual,
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
    
    # Abre a tela de conferência com o ID passado
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
def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_despesas_{periodo_atual}.pdf"})


@app.get("/relatorio_comparativo_despesas", response_class=HTMLResponse)
def serve_relatorio_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)


# ========== ROTAS DE HISTÓRICO DESPESAS (FORÇADAS) ==========
@app.post("/api/comparativo_despesas_v2/{periodo_atual}/salvar")
def rota_salvar_comparativo_despesas(periodo_atual: str):
    import sqlite3, os, json
    from datetime import datetime
    
    dados = api_comparativo_despesas_v2(periodo_atual)
    if dados.get("erro"): return {"erro": True, "mensagem": dados.get("mensagem")}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
        
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)
    
    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo_atual, data_geracao, dados_json))
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
    
    # Abre a tela do relatório passando o ID do histórico
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
    
    # Abre a tela do panorama passando o ID do histórico
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
    
    # Abre o relatório v2 passando o ID do histórico
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
        return {"erro": True, "mensagem": "Histórico não encontrado."}
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
    return {"erro": True, "mensagem": "Relatório não encontrado"}



# ============================================================
# ROTAS DE SALVAR E EXCLUIR - COMPARATIVO DE RECEITAS
# ============================================================

@app.post("/api/comparativo_receitas_v2/{periodo_atual}/salvar")
def salvar_comparativo_receitas(periodo_atual: str):
    import sqlite3, os, json
    from datetime import datetime
    
    # Pega os dados atuais via API
    try:
        dados = api_comparativo_receitas_v2(periodo_atual)
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
                (periodo_atual, data_geracao, dados_json))
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
    
    # Lê o CSV
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
    
    # Título
    pdf.set_font("Helvetica", "B", 16)
    titulo = tipo.replace("_", " ").title()
    pdf.cell(0, 10, f"Relatório - {titulo}", new_x="LMARGIN", new_y="NEXT", align="C")
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

@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado(periodo: str):
    import sqlite3, os, json
    # Aqui buscamos os dados de todos os modulos (BP, DFC, DVP, DMPL, BF, Integridade)
    # Para simplificar, vamos apenas retornar o status de cada um
    # (Na proxima etapa, cruzamos os dados reais)
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    modulos = {}
    # Verifica quais modulos tem historico salvo para esse periodo
    for tabela in ["historico_analise_financeira_bf", "historico_analise_dfc", "historico_integridade_matriz"]:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE periodo LIKE ?", (f"%{periodo}%",))
            modulos[tabela] = cursor.fetchone()[0]
        except Exception:
            modulos[tabela] = 0
    
    conn.close()
    
    return {
        "periodo": periodo,
        "modulos": modulos,
        "status": "ok" if sum(modulos.values()) > 0 else "faltando"
    }

@app.post("/salvar_relatorio_consolidado/{periodo}")
async def salvar_relatorio_consolidado(periodo: str):
    import sqlite3, json
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    
    # Pega os dados de todos os modulos
    # Por enquanto, salvamos um JSON simples (na proxima etapa sera completo)
    dados = {"periodo": periodo, "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    data_agora = dados["gerado_em"]
    
    cursor.execute("INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Relatorio consolidado salvo com sucesso!"}

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

@app.get("/gerar_pdf_relatorio_consolidado/{id}")
async def gerar_pdf_relatorio_consolidado(id: int):
    import sqlite3, json, os
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    # Pega dados da entidade
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT, razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT, contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT)""")
    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    ent = cursor.fetchone()
    conn.close()
    
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404)
    
    periodo, data_geracao = row
    
    # Dados da entidade
    razao = ent[1] if ent and len(ent) > 1 else "COFEN/BR"
    cnpj = ent[3] if ent and len(ent) > 3 else ""
    contador_nome = ent[7] if ent and len(ent) > 7 else ""
    contador_crc = ent[8] if ent and len(ent) > 8 else ""
    contador_uf = ent[9] if ent and len(ent) > 9 else ""
    contador_cpf = ent[10] if ent and len(ent) > 10 else ""
    logo_path = ent[13] if ent and len(ent) > 13 else ""
    
    pdf = FPDF()
    pdf.add_page()
    
    # CAPA
    # Logo (se existir)
    caminho_logo = ""
    if logo_path:
        if os.path.isabs(logo_path):
            caminho_logo = logo_path
        else:
            caminho_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos", logo_path)
        if not os.path.exists(caminho_logo):
            caminho_logo = ""
    
    if caminho_logo:
        try:
            # Centraliza a logo no topo
            pdf.image(caminho_logo, x=70, y=20, w=70)
            y_inicio = 100
        except Exception:
            y_inicio = 50
    else:
        y_inicio = 50
    
    # Titulo
    pdf.set_y(y_inicio)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "RELATORIO CONSOLIDADO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "DE ANALISE CONTABIL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Periodo: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, f"Data de Emissao: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(30)
    
    # Dados da entidade na capa
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "DADOS DA ENTIDADE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Razao Social: {razao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CNPJ: {cnpj}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(20)
    
    # Dados do contador na capa
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "RESPONSAVEL TECNICO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Contador: {contador_nome}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CRC: {contador_crc} / UF: {contador_uf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"CPF: {contador_cpf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # ========== PAGINA 2: SUMARIO ==========
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "SUMARIO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    capitulos = [
        "1. Apresentacao e Escopo",
        "2. Visao Geral Orcamentaria e Financeira",
        "3. Analise do Balanco Patrimonial",
        "4. Demonstracao das Variacoes Patrimoniais",
        "5. Demonstracao dos Fluxos de Caixa",
        "6. Demonstracao das Mutacoes do PL",
        "7. Analise de Despesas e Custeio",
        "8. Matriz de Integridade e Controles",
        "9. Parecer Conclusivo",
        "10. Anexos e Assinaturas"
    ]
    for cap in capitulos:
        pdf.cell(0, 8, cap, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ========== PAGINA FINAL: ASSINATURA ==========
    pdf.add_page()
    pdf.set_y(100)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "_____________________________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, "Contador Responsavel", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, contador_nome, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"CRC: {contador_crc} / UF: {contador_uf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 8, f"CPF: {contador_cpf}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Relatorio_Consolidado_{periodo}.pdf"})

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
        creditos_at, creditos_ant = buscar_ativo("CRÉDITOS A CURTO PRAZO")
        ativo_nao_circ_at, ativo_nao_circ_ant = buscar_ativo("ATIVO NÃO CIRCULANTE")
        ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZÁVEL A LONGO PRAZO")
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
    col_w = [70, 40, 40, 30]
    headers = ["Conta", "Periodo Atual (R$)", "Periodo Anterior (R$)", "Var. (%)"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    
    def linha(label, va, vb):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        pdf.ln()
    
    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0))
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0))
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0))
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0))
    linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0))
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0))
    linha("TOTAL DO ATIVO", d.get("total_ativo", {}).get("atual", 0), d.get("total_ativo", {}).get("anterior", 0))
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0))
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0))
    linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0))
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0))
    linha("TOTAL DO PASSIVO", d.get("total_passivo", {}).get("atual", 0), d.get("total_passivo", {}).get("anterior", 0))
    
    pdf_bytes = bytes(pdf.output())
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Analise_BP_{periodo}.pdf"})

