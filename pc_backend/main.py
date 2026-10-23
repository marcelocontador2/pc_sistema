from fastapi import FastAPI
from historico_integridade import router as historico_router
from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Response, Form
from fastapi.staticfiles import StaticFiles
from historico_integridade import router as historico_router
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import shutil
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, shutil, io, glob, csv
import psycopg2
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

app = FastAPI(title="PC - Prestacao de Contas API")
# Conecta as rotas do historico de integridade
app.include_router(historico_router)

# Liberar acesso aos arquivos HTML/CSS/JS do Frontend
import os
pasta_frontend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend")
if os.path.exists(pasta_frontend):
    app.mount("/pc_frontend", StaticFiles(directory=pasta_frontend), name="pc_frontend")

from integridade import router as integridade_router
app.include_router(integridade_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database",
             "user": "postgres", "password": "pc_admin_2026"}

UPLOAD_DIR = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
FRONTEND_DIR = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open(os.path.join(FRONTEND_DIR, "index.html"), encoding="utf-8") as f:
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    # Lê mantendo TODAS as colunas vazias (inclusive as do início e do meio)
    linhas = content.splitlines()
    for linha in linhas:
        if not linha.strip():
            continue
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in linha.split(';')]
        
        max_cols = 9 if tipo == "DMPL" else 8
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
            
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
    import io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    # Leitura manual para não perder colunas vazias no meio
    linhas = content.splitlines()
    for linha in linhas:
        if not linha.strip():
            continue
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in linha.split(';')]
        
        max_cols = 9 if tipo == "DMPL" else 8
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
            
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    # Lê o CSV mantendo todas as colunas
    reader = csv.reader(io.StringIO(content), delimiter=';')
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        if not any(clean):
            continue
        
        # Preenche até 9 colunas para o DMPL, e até 8 para os outros
        max_cols = 9 if tipo == "DMPL" else 8
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
            
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    reader = csv.reader(io.StringIO(content), delimiter=';')
    # DMPL tem 9 colunas. Os outros mantêm as suas.
    max_cols = 9 if tipo == "DMPL" else 8
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        # Se a linha for totalmente vazia, pula
        if not any(clean):
            continue
        # Garante o número de colunas
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    reader = csv.reader(io.StringIO(content), delimiter=';')
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        if not any(clean):
            continue
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    reader = csv.reader(io.StringIO(content), delimiter=';')
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        if not any(clean):
            continue
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    reader = csv.reader(io.StringIO(content), delimiter=';')
    # O Balanco Financeiro tem 8 colunas. Os outros têm 6 ou 7.
    max_cols = 8 if tipo in ["BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO"] else 6
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        if not any(clean):
            continue
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
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
    import csv, io
    dados = []
    content = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if not content:
        return dados

    reader = csv.reader(io.StringIO(content), delimiter=';')
    max_cols = 7 if tipo == "BALANCO_ORCAMENTARIO" else 6
    for row in reader:
        clean = [str(c).replace('\n',' ').replace('\r',' ').replace('\ufeff','').strip() for c in row]
        if not any(clean):
            continue
        clean = clean[:max_cols]
        while len(clean) < max_cols:
            clean.append('')
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
                content = f.read()
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

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(...),
    ano: int = Form(...),
    periodo_tipo: str = Form(...),
    periodo_valor: str = Form(...)
):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV.")
        
        conteudo_arquivo = await file.read()
        try:
            texto_arquivo = conteudo_arquivo.decode('utf-8-sig')
        except UnicodeDecodeError:
            texto_arquivo = conteudo_arquivo.decode('latin-1')
        
        # Normaliza o texto: maiúsculo, substitui "Ç" por "C" e remove acentos para facilitar a busca
        import unicodedata
        texto_normalizado = texto_arquivo.upper()
        texto_normalizado = texto_normalizado.replace("Ç", "C")
        texto_normalizado = ''.join(c for c in unicodedata.normalize('NFD', texto_normalizado) if unicodedata.category(c) != 'Mn')
        # Trata o erro de encoding comum (ex: Balanįo -> BALANIO)
        texto_normalizado = texto_normalizado.replace("į", "I").replace("Į", "I").replace("ő", "O").replace("Ő", "O")

        # Regras de validação estritas
        if tipo_relatorio == "BALANCETE":
            if "BALANCETE" not in texto_normalizado:
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Balancete'.")
                
        elif tipo_relatorio == "BALANCO_PATRIMONIAL":
            if not ("BALAN" in texto_normalizado and "PATRIMONIAL" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Balanço Patrimonial'.")
                
        elif tipo_relatorio == "BALANCO_FINANCEIRO":
            if not ("BALAN" in texto_normalizado and "FINANCEIRO" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Balanço Financeiro'.")
                
        elif tipo_relatorio == "BALANCO_ORCAMENTARIO":
            if not ("BALAN" in texto_normalizado and "ORCAMENTARIO" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Balanço Orçamentário'.")
                
        elif tipo_relatorio == "DFC":
            if not ("FLUXO DE CAIXA" in texto_normalizado or "DEMONSTRACAO DO FLUXO" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Demonstração do Fluxo de Caixa'.")
                
        elif tipo_relatorio == "DVP":
            if not ("VARIACOES PATRIMONIAIS" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Variações Patrimoniais'.")
                
        elif tipo_relatorio == "DMPL":
            if not ("MUTACOES" in texto_normalizado or "MUTACOES DO PATRIMONIO" in texto_normalizado):
                raise HTTPException(status_code=400, detail="Arquivo rejeitado! O arquivo não contém o título 'Demonstração das Mutações do Patrimônio Líquido'.")

        await file.seek(0)
        
        nome_padronizado = f"{tipo_relatorio}_{ano}_{periodo_tipo}_{periodo_valor}.csv"
        caminho_final = os.path.join(UPLOAD_DIR, nome_padronizado)
        
        with open(caminho_final, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        data_agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO importacoes (tipo_relatorio, ano, periodo_tipo, periodo_valor, nome_original, caminho_arquivo, data_importacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tipo_relatorio, ano, periodo_tipo, periodo_valor, file.filename, caminho_final, data_agora))
        conn.commit()
        conn.close()
        
        return {"mensagem": "Upload realizado com sucesso!", "arquivo": nome_padronizado}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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

        content = ""
        for enc in ["utf-8-sig", "utf-8", "latin-1"]:
            try:
                with open(csv_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=False)

        # ---------- LAYOUTS ----------
        if tipo == "BALANCETE":
            col_w   = [125, 0, 38, 38, 38, 38]
            headers = ["CONTA", "", "SALDO ANTERIOR", "DÉBITOS", "CRÉDITOS", "SALDO"]
            titulo_pdf = "Balancete Contábil"
        elif tipo == "BALANCO_PATRIMONIAL":
            col_w   = [85, 30, 85, 30, 0, 0]
            headers = ["ESPECIFICAÇÃO (ATIVO)", "Exercício Atual", "ESPECIFICAÇÃO (PASSIVO)", "Exercício Atual", "", ""]
            titulo_pdf = "Balanço Patrimonial"
        elif tipo == "BALANCO_FINANCEIRO":
            col_w   = [68, 28, 28, 68, 28, 28] 
            headers = ["ESPECIFICAÇÃO (INGRESSOS)", "Exercício Atual", "Exercício Anterior", "ESPECIFICAÇÃO (DISPÊNDIOS)", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Balanço Financeiro"
        elif tipo == "BALANCO_ORCAMENTARIO":
            col_w   = [70, 32, 32, 34, 34, 34, 41]
            headers = ["ESPECIFICAÇÃO", "PREVISÃO INICIAL", "PREVISÃO ATUALIZADA", "RECEITA REALIZADA", "SALDO", "DESPESAS", "SALDO FINAL"]
            titulo_pdf = "Balanço Orçamentário"
        elif tipo == "DMPL":
            col_w   = [60, 24.5, 24.5, 24.5, 24.5, 24.5, 24.5, 34, 35] 
            headers = [
                "ESPECIFICAÇÃO", "PATRIMÔNIO SOCIAL", "ADIANTAMENTO P/ AUMENTO", 
                "RESERVAS DE CAPITAL", "AJUSTES DE AVALIAÇÃO", "RESERVAS DE LUCROS", 
                "DEMAIS RESERVAS", "RESULTADOS ACUMULADOS", "TOTAL"
            ]
            titulo_pdf = "Demonstração das Mutações do Patrimônio Líquido"
        elif tipo == "DFC":
            col_w   = [160, 0, 0, 60, 57]
            headers = ["ESPECIFICAÇÃO", "", "", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Demonstração do Fluxo de Caixa"
        elif tipo == "DVP":
            # Layout DVP: Desc Ativa | Atual | Anterior | Desc Passiva | Atual | Anterior
            col_w   = [70, 25, 25, 70, 25, 25]
            headers = ["VARIAÇÕES AUMENTATIVAS", "Exercício Atual", "Exercício Anterior", "VARIAÇÕES DIMINUTIVAS", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Demonstração das Variações Patrimoniais"
        else:
            col_w   = [72, 30, 28, 72, 40, 35]
            headers = ["ESPECIFICAÇÃO", "Exercício Atual", "Exercício Anterior", "ESPECIFICAÇÃO", "Exercício Atual", "Exercício Anterior"]
            titulo_pdf = "Balanço Comparativo"

        def draw_header(is_first_page=False):
            if is_first_page:
                pdf.set_fill_color(0, 114, 186)
                pdf.rect(10, 10, 277, 20, 'F')
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_xy(15, 12)
                pdf.cell(0, 6, "COFEN/BR - Conselho Federal de Enfermagem", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_x(15)
                pdf.cell(0, 5, "CNPJ: 47.217.146/0001-57", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_xy(200, 12)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(85, 6, f"Período: {periodo_formatado}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.set_font("Helvetica", "", 9)
                pdf.set_x(200)
                pdf.cell(85, 5, titulo_pdf, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(12)
            else:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
                pdf.ln(2)
            
            pdf.set_fill_color(230, 240, 250)
            pdf.set_font("Helvetica", "B", 6) 
            pdf.set_text_color(0, 0, 0)
            
            start_y = pdf.get_y()
            x_start = pdf.get_x()
            
            for j, h in enumerate(headers):
                if col_w[j] > 0:
                    pdf.rect(pdf.get_x(), start_y, col_w[j], 10, style='DF')
                    pdf.set_xy(pdf.get_x(), start_y + 1)
                    pdf.multi_cell(col_w[j], 4, h, border=0, align="C")
                    pdf.set_xy(x_start + sum(col_w[:j+1]), start_y)
            
            pdf.set_xy(x_start, start_y + 10)

        pdf.add_page()
        draw_header(is_first_page=True)

        def draw_row(row, is_header, is_total, idx):
            num_lines = 1
            for j in range(len(col_w)):
                if col_w[j] > 0 and j < len(row):
                    txt = str(row[j]).encode('latin-1', 'replace').decode('latin-1') or " "
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
                txt = str(row[j]).encode('latin-1', 'replace').decode('latin-1')

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
                    pdf.multi_cell(col_w[j], 5, txt, border=0, align="L")
                else:
                    center_y = y + (actual_h - 5) / 2
                    pdf.set_xy(x + sum(col_w[:j]), center_y)
                    pdf.cell(col_w[j], 5, txt, align="R", border=0)
            
            pdf.set_xy(x, y + actual_h)

        # =======================================================
        # LÓGICA ESPECÍFICA PARA O DVP
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
            res_1, res_2 = buscar_valores("Resultado do período")
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
                    if "ESPECIFICAÇÃO" in joined and "EXERCÍCIO ATUAL" in joined:
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

                if is_header: pdf.set_font("Helvetica", "B", 7.5)
                elif is_total: pdf.set_font("Helvetica", "B", 7)
                else:          pdf.set_font("Helvetica", "", 7)

                draw_row(row, is_header, is_total, idx)

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
            raise HTTPException(status_code=404, detail="CSV nÃ£o encontrado.")
            
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
        ws['A2'] = f"CNPJ: 47.217.146/0001-57   |   PerÃ­odo: {periodo}/{ano}"
        ws['A2'].font = Font(size=10, color="FFFFFF")
        ws['A2'].fill = PatternFill(start_color="0072BA", end_color="0072BA", fill_type="solid")
        ws['A2'].alignment = Alignment(vertical="center")

        # CabeÃ§alho
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
            is_header = any(k in row[0].upper() for k in ["ATIVO", "PASSIVO", "PATRIMÃ”NIO", "RECEITAS", "DESPESAS", "INGRESSOS"])
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
            raise HTTPException(status_code=404, detail="CSV nÃ£o encontrado.")
        
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
                            if any(k in text.upper() for k in ["ATIVO", "PASSIVO", "TOTAL", "ESPECIFICAÃ‡ÃƒO", "RECEITAS"]):
                                r.font.bold = True
                            if j > 0:
                                pr.alignment = PP_ALIGN.RIGHT

        buf = io.BytesIO(); prs.save(buf); buf.seek(0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PPTX: {e}")
        
    return Response(content=buf.getvalue(), media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="relatorio_{tipo}_{ano}.pptx"'})

@app.post("/upload")
async def upload_arquivo(file: UploadFile = File(...)):
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as b: shutil.copyfileobj(file.file, b)
    return {"filename": file.filename, "status": "sucesso"}


import json
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
@app.get("/salvar_integridade/{periodo}")
async def salvar_integridade(periodo: str):
    try:
        # Chama a função do integridade.py
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        
        # Converte para JSON para salvar no banco
        json_resultado = json.dumps(dados)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico_integridade (periodo, data_geracao, resultado_json)
            VALUES (?, ?, ?)
        ''', (periodo, data_agora, json_resultado))
        conn.commit()
        conn.close()
        
        return {"mensagem": "Integridade gerada e salva com sucesso!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rota que LISTA todos os históricos salvos
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)












































# --- IMPORTACAO DAS ROTAS EXTRA ---
import rotas_extra

@app.get("/painel_integridade_html/{periodo}")
async def painel_integridade_html(periodo: str):
    from fastapi.responses import HTMLResponse
    try:
        # Importa a função do nosso módulo de integridade
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        analises = dados.get("analises", [])
        
        html = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Integridade</title>"
        html += "<style>body { font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; } .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); } table { width: 100%; border-collapse: collapse; margin-bottom: 15px; } td { padding: 8px 0; border-bottom: 1px solid #eee; } .status-ok { color: green; border-left: 5px solid green; } .status-erro { color: red; border-left: 5px solid red; }</style></head><body>"
        html += "<h2>Análises de Integridade - " + periodo + "</h2>"
        
        if not analises:
            html += "<p>Nenhuma análise encontrada.</p>"
        
        for a in analises:
            classe = "status-ok" if a["status"] == "OK" else "status-erro"
            html += f"<div class='card {classe}'>"
            html += f"<h3>{a['titulo']}</h3>"
            html += f"<p style='color: #666;'>{a['conceito']}</p>"
            html += "<table>"
            for linha in a["tabela"]:
                html += f"<tr><td>{linha['label']}</td><td style='text-align: right; font-weight: bold;'>{linha['valor']}</td></tr>"
            html += "</table>"
            html += f"<div style='color: {'green' if a['status']=='OK' else 'red'};'>{a['mensagem']}</div>"
            html += "</div>"
            
        html += "</body></html>"
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<h3>Erro ao carregar integridade: {e}</h3>", status_code=500)
