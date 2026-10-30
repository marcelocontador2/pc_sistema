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
        for p in linhas:
            if len(p) > coluna and termo.upper() in p[0].upper():
                return abs(_limpar_valor(p[coluna]))
        return 0.0

    ativo_total = buscar(l_bp, "TOTAL", 1)
    passivo_total = buscar(l_bp, "TOTAL", 3)
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

@app.get("/api/panorama/{periodo}")
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
                for celula in p:
                    for termo in termos:
                        if termo.upper() in str(celula).upper():
                            if len(p) > coluna:
                                try:
                                    v = abs(_limpar_valor(p[coluna]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0

        # === BP ===
        passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 3)
        pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"], 3)
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

@app.get("/gerar_pdf_panorama/{id}")
async def gerar_pdf_panorama(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import httpx, sqlite3, json, os
        
        # 1. Pega o período do histórico salvo
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_panorama WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
        
        periodo, data_geracao, json_str = row

        # 2. Consome a API do Painel para pegar os valores EXATOS do momento
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:8000/api/panorama/{periodo}")
            if response.status_code != 200:
                raise Exception(f"Erro ao buscar dados do painel: {response.status_code}")
            dados = response.json()
        
        # 3. Busca o valor do Caixa diretamente do BP para garantir que não venha zerado
        # Usa a função _calc_liquidez que já sabe buscar o caixa no BP
        dados_bp = _calc_liquidez(periodo)
        caixa_bp = dados_bp.get("valores", {}).get("caixa", 0) if dados_bp else 0

        # 4. Gera o PDF
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, "P A N O R A M A", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font("helvetica", "B", 22)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, f"Resultados Gerais - {periodo.replace('-', ' ').title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)

        def fmt_mi(v): return f"R$ {v/1000000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")

        def card(x, y, w, h, valor, label):
            pdf.set_fill_color(233, 242, 250)
            pdf.rect(x, y, w, h, style='F')
            pdf.set_xy(x + 5, y + 5)
            pdf.set_font("helvetica", "B", 20)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(w - 10, 10, valor, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_xy(x + 5, y + 18)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w - 10, 5, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Linha 1 (Topo)
        card(15, 50, 85, 35, fmt_mi(caixa_bp), "Caixa e Equivalente (BP)")
        card(105, 50, 85, 35, fmt_mi(dados.get("ativo_total", 0)), "Ativo Total")
        card(195, 50, 85, 35, fmt_mi(dados.get("passivo_total", 0)), "Passivo Total")
        
        card(15, 95, 85, 35, fmt_mi(dados.get("patrimonio_liquido", 0)), "Patrimônio Líquido")
        card(105, 95, 85, 35, fmt_mi(dados.get("receita_realizada", 0) or dados.get("receitas_realizadas", 0)), "Receitas Realizadas (BO)")
        card(195, 95, 85, 35, fmt_mi(dados.get("despesa_empenhada", 0) or dados.get("despesas_empenhadas", 0)), "Despesas Empenhadas (BO)")

        card(15, 140, 85, 35, fmt_mi(dados.get("superavit_orcamentario", 0)), "Superávit/Déficit Orçamentário")
        card(105, 140, 85, 35, fmt_mi(dados.get("superavit_patrimonial", 0)), "Superávit/Déficit Patrimonial")
        card(195, 140, 85, 35, fmt_mi(dados.get("superavit_financeiro", 0)), "Superávit/Déficit Financeiro")

        pdf.set_y(185)
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 5, "Todos os demonstrativos estão equilibrados e consistentes entre si. Equação patrimonial: Ativo = Passivo + PL.", align="L")
        
        pdf.set_y(-20)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 10, "Cofen - Analise das Demonstrações Contábeis", align="L")
        pdf.cell(0, 10, "03", align="R")

        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Resumo_{periodo.replace('-', '_')}.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def salvar_integridade_matriz(periodo: str):
    try:
        from matriz_integridade import gerar_matriz
        dados = await gerar_matriz(periodo)
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", 
                       (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"mensagem": "Matriz salva!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_integridade_matriz WHERE id=?", (id,))
        row = cur.fetchone(); conn.close()
        if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
        periodo, data_geracao, json_str = row
        d = json.loads(json_str)
        matriz = d.get("matriz", [])

        # A3 PAISAGEM (420x297) para caber as 9 colunas com folga
        pdf = FPDF(orientation="L", unit="mm", format="A3")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("helvetica", "B", 18); pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 12, f"Matriz de Integridade - {periodo.replace('-', ' ').title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "I", 11); pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(6)

        # Larguras proporcionais para A3 (util ~400mm)
        # NOMENCLATURA 100, 7 colunas de 38 = 266, CONF 34 = 400 total
        colunas = ["NOMENCLATURA", "BALANCETE", "BP", "BF", "BO", "DFC", "DVP", "DMPL", "CONF."]
        larguras = [100, 38, 38, 38, 38, 38, 38, 38, 34]

        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(0, 86, 179); pdf.set_text_color(255, 255, 255)
        for i, col in enumerate(colunas):
            pdf.cell(larguras[i], 9, col, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("helvetica", "", 8); pdf.set_text_color(0, 0, 0)
        for linha in matriz:
            pdf.cell(larguras[0], 7, str(linha.get('item', '')), border=1, align="L")
            for key, index in zip(["balancete", "bp", "bf", "bo", "dfc", "dvp", "dmpl"], range(1, 8)):
                pdf.cell(larguras[index], 7, str(linha.get(key, '-')), border=1, align="R")
            conf = str(linha.get('conf', ''))
            pdf.set_text_color(0, 128, 0) if conf == "OK" else pdf.set_text_color(255, 0, 0)
            pdf.cell(larguras[8], 7, conf, border=1, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln()

        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Integridade_{periodo}.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analise_orcamentaria_bo/{periodo}")
async def api_analise_orcamentaria_bo(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from matriz_integridade import _get_csv
        import os
        caminho_check = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Orçamentário"]}
        
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        import os
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
        import os
        caminho_check = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Orçamentário"]}
        
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        import os
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

@app.get("/api/analise_financeira_bf/{periodo}")
async def api_analise_financeira_bf(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from matriz_integridade import _get_csv
        import os
        caminho_check = _get_csv("BALANCO_FINANCEIRO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Financeiro"]}
        
        from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        import os
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







@app.get("/gerar_pdf_analise_financeira_bf/{id}")
async def gerar_pdf_analise_financeira_bf(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json, sqlite3
        
        # 1. Busca o periodo no banco
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo FROM historico_analise_financeira_bf WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo_atual = row[0].split(' vs ')[0]
        
        # 2. Busca os dados da API (que ja sabemos que tem a estrutura correta)
        dados_resp = await api_analise_financeira_bf(periodo_atual)
        if dados_resp.get("erro"): raise HTTPException(status_code=400, detail="Erro nos dados")
        
        d = dados_resp["dados"]  # Aqui estao os dados: receita_realizada, etc.
        
        # 3. Extrai os valores (atual e anterior) de cada indicador
        def get_val(chave, tipo):
            obj = d.get(chave, {})
            return obj.get(tipo, 0) if isinstance(obj, dict) else 0
        
        receita_realizada = {"atual": get_val("receita_realizada", "atual"), "anterior": get_val("receita_realizada", "anterior")}
        despesa_orcamentaria = {"atual": get_val("despesa_orcamentaria", "atual"), "anterior": get_val("despesa_orcamentaria", "anterior")}
        recebimentos_extra = {"atual": get_val("recebimentos_extra", "atual"), "anterior": get_val("recebimentos_extra", "anterior")}
        pagamentos_extra = {"atual": get_val("pagamentos_extra", "atual"), "anterior": get_val("pagamentos_extra", "anterior")}
        saldo_anterior = {"atual": get_val("saldo_anterior", "atual"), "anterior": get_val("saldo_anterior", "anterior")}
        saldo_seguinte = {"atual": get_val("saldo_seguinte", "atual"), "anterior": get_val("saldo_seguinte", "anterior")}
        total_ingressos = {"atual": get_val("total_ingressos", "atual"), "anterior": get_val("total_ingressos", "anterior")}
        total_dispendios = {"atual": get_val("total_dispendios", "atual"), "anterior": get_val("total_dispendios", "anterior")}
        
        # 4. Gera o grafico (Atual primeiro)
        labels = ["Saldo Inicial", "Saldo Final", "Variação"]
        ant = [saldo_anterior["anterior"], saldo_seguinte["anterior"], saldo_seguinte["anterior"] - saldo_anterior["anterior"]]
        atu = [saldo_anterior["atual"], saldo_seguinte["atual"], saldo_seguinte["atual"] - saldo_anterior["atual"]]
        
        fig, ax = plt.subplots(figsize=(6, 2.8), dpi=150)
        x = range(len(labels))
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
        
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_fin_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        
        # 5. Monta o PDF
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
        pdf.cell(0, 10, "Balanco Financeiro Comparativo", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo de Referencia: {periodo_atual}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(8)
        
        # Tabela
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
        
        ind = [
            ("Receita Realizada (Ingressos)", receita_realizada),
            ("Despesa Orcamentaria", despesa_orcamentaria),
            ("Recebimentos Extraorcamentarios", recebimentos_extra),
            ("Pagamentos Extraorcamentarios", pagamentos_extra),
            ("Saldo em Especie do Exerc. Anterior", saldo_anterior),
            ("Saldo em Especie para o Exerc. Seguinte", saldo_seguinte),
            ("Total (Ingressos)", total_ingressos),
            ("Total (Dispendios)", total_dispendios),
        ]
        
        for nome, val in ind:
            va = val["atual"]
            vb = val["anterior"]
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va), border=1, align="R")
            pdf.cell(45, 7, fmt(vb), border=1, align="R")
            
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        
        # Grafico
        pdf.ln(8)
        y_atual = pdf.get_y()
        pdf.image(img_path, x=30, y=y_atual, w=110)
        
        # Conclusao
        pdf.set_xy(150, y_atual)
        pdf.set_font(f_family, "B", 10)
        pdf.cell(0, 6, "Principais conclusoes:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(150)
        pdf.set_font(f_family, "", 8)
        txt_conclusao = f"O caixa apresentou variacao de R$ {fmt(saldo_seguinte['atual'] - saldo_anterior['atual'])}. Ingressos e Dispendios estao equilibrados."
        pdf.multi_cell(90, 4, txt_conclusao)
        
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=analise_financeira_{id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise_financeira_bf")
async def serve_analise_financeira_bf():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_financeira_bf.html")
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
        import os
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

@app.get("/api/analise_patrimonial/{periodo}")
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
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json, sqlite3
        
        # 1. Busca o periodo no banco
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, resultado_json FROM historico_analise_patrimonial WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, d_json = row
        d = json.loads(d_json)
        
        # 2. Extrai os dados da estrutura retornada (que tem 'atual' e 'anterior' dentro de cada chave)
        # A estrutura é: { "variacoes_ativas": { "atual": X, "anterior": Y }, ... }
        def get_val(chave, tipo):
            obj = d.get(chave, {})
            return obj.get(tipo, 0) if isinstance(obj, dict) else 0
        
        # 3. Gera o grafico (Atual primeiro)
        labels = ["Variações Ativas", "Variações Diminutivas", "Superávit Patrimonial"]
        ant = [get_val("variacoes_ativas", "anterior"), get_val("variacoes_diminutivas", "anterior"), get_val("superavit_patrimonial", "anterior")]
        atu = [get_val("variacoes_ativas", "atual"), get_val("variacoes_diminutivas", "atual"), get_val("superavit_patrimonial", "atual")]
        
        fig, ax = plt.subplots(figsize=(5, 2.0), dpi=150)
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], atu, width=0.4, label="Atual", color="#003366")
        ax.bar([i + 0.2 for i in x], ant, width=0.4, label="Anterior", color="#4a90e2")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.legend(loc="upper right", fontsize=8, frameon=False)
        formatter = ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:,.0f} Mi")
        ax.yaxis.set_major_formatter(formatter)
        ax.tick_params(axis="y", labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_pat_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        
        # 4. Monta o PDF
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
        pdf.cell(0, 10, "Demonstração das Variações Patrimoniais (DVP)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Período de Referência: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
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
        
        ind = [
            ("Variações Ativas", "variacoes_ativas"),
            ("Transferências Recebidas", "transf_recebidas"),
            ("Reversão de Provisões", "reversao_provisoes"),
            ("Variações Diminutivas", "variacoes_diminutivas"),
            ("Pessoal e Encargos", "pessoal_encargos"),
            ("Serviços de Terceiros", "servicos_terceiros"),
            ("Transferências Concedidas", "transf_concedidas"),
            ("Superávit Patrimonial", "superavit_patrimonial"),
        ]
        
        for nome, chave in ind:
            va = get_val(chave, "atual")
            vb = get_val(chave, "anterior")
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            
            is_bold = "B" if "Superávit" in nome else ""
            pdf.set_font(f_family, is_bold, 9)
            
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va), border=1, align="R")
            pdf.cell(45, 7, fmt(vb), border=1, align="R")
            
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font(f_family, "", 9)
        
        # Grafico e Card da Margem
        pdf.ln(8)
        y_atual = pdf.get_y()
        pdf.image(img_path, x=30, y=y_atual, w=100)
        
        # Card da Margem
        pdf.set_xy(140, y_atual)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 10)
        margem_at = d.get("margem_patrimonial", {}).get("atual", 0)
        margem_ant = d.get("margem_patrimonial", {}).get("anterior", 0)
        pdf.multi_cell(60, 8, f"Margem Patrimonial:\n{margem_ant:.2f}% -> {margem_at:.2f}%\n\n(Superávit / Variações Ativas)", border=0, fill=True, align="C")
        
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=analise_patrimonial_{id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            "Lei Complementar no 101/2000 (LRF)",
            "Manual de Contabilidade Aplicada ao Setor Publico (MCASP)",
            "Resolucao COFEN no 340/2008 (Regulamento da Administracao Financeira e Contabil)",
            "Resolucao COFEN no 764/2024 (Prestacao de Contas)",
            "Normas Brasileiras de Contabilidade - Setor Publico (NBC TSP)"
        ]
        
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

@app.get("/analise_custo_pessoal")
async def serve_analise_custo_pessoal():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_custo_pessoal.html")
    return FileResponse(caminho)


@app.get("/api/analise_custo_pessoal/{periodo}")
async def api_analise_custo_pessoal(periodo: str):
    # Regra de integridade: verifica se os arquivos existem
    from matriz_integridade import _get_csv
    pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
    faltando = [p for p in pecas_obrigatorias if not _get_csv(p, periodo)]
    if faltando:
        return {"erro": "faltando", "pecas": faltando}
    
    return {"erro": False, "mensagem": "Dados de Custo de Pessoal em implementação."}









    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    def ler_periodo_interno(caminho):
        try:
            with open(caminho, "r", encoding="latin-1") as f:
                leitor = csv.reader(f, delimiter=";")
                for i, linha in enumerate(leitor):
                    if i > 10: break
                    texto = " ".join(linha)
                    match = re.search(r"Período:\s*(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})", texto)
                    if match:
                        return match.group(0)
        except:
            pass
        return None
    
    def extrair_periodo(texto):
        if not texto: return None
        match = re.search(r"a\s*(\d{2})/(\d{2})/(\d{4})", texto)
        if match:
            mes_final = int(match.group(2))
            ano = int(match.group(3))
            if mes_final <= 3: trimestre = 1
            elif mes_final <= 6: trimestre = 2
            elif mes_final <= 9: trimestre = 3
            else: trimestre = 4
            return f"{ano}-TRIMESTRE-{trimestre}"
        return None
    
    def periodos_anteriores_necessarios(periodo_str):
        partes = periodo_str.split("-")
        ano = int(partes[0])
        tipo = partes[1]
        valor = int(partes[2])
        
        meses_acumulados = valor * 3
        meses_faltando = 12 - meses_acumulados
        periodos = []
        
        while meses_faltando > 0:
            valor -= 1
            if valor < 1:
                ano -= 1
                valor = 4
            periodos.append(f"{ano}-{tipo}-{valor}")
            meses_faltando -= 3
        
        return periodos
    
    arquivos = [f for f in os.listdir(pasta) if f.startswith("BALANCO_ORCAMENTARIO_") and f.endswith(".csv")]
    caminho_atual = None
    for arq in arquivos:
        caminho = os.path.join(pasta, arq)
        texto = ler_periodo_interno(caminho)
        periodo_arq = extrair_periodo(texto)
        if periodo_arq == periodo:
            caminho_atual = caminho
            break
    
    if not caminho_atual:
        return {"erro": "faltando", "pecas": [f"BALANCO_ORCAMENTARIO ({periodo})"]}
    
    periodos_necessarios = periodos_anteriores_necessarios(periodo)
    caminhos_anteriores = []
    for p in periodos_necessarios:
        encontrado = None
        for arq in arquivos:
            caminho = os.path.join(pasta, arq)
            texto = ler_periodo_interno(caminho)
            periodo_arq = extrair_periodo(texto)
            if periodo_arq == p:
                encontrado = caminho
                break
        if not encontrado:
            return {"erro": "faltando", "pecas": [f"BALANCO_ORCAMENTARIO ({p})"]}
        caminhos_anteriores.append(encontrado)
    
    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0
    
    def extrair_bo(caminho):
        valores = {"pessoal": 0.0, "outras_desp": 0.0, "terceirizacao": 0.0, "sentencas_trabalhistas": 0.0, "receitas_correntes": 0.0}
        with open(caminho, "r", encoding="latin-1") as f:
            leitor = list(csv.reader(f, delimiter=";"))
        for i, linha in enumerate(leitor):
            if len(linha) < 8: continue
            nome = linha[0].strip().upper()
            if "RECEITAS CORRENTE" in nome and "OUTRAS" not in nome:
                valores["receitas_correntes"] = limpar(linha[6])
            if "PESSOAL E ENCARGOS SOCIAIS" in nome and "OUTRAS" not in nome:
                valores["pessoal"] += limpar(linha[5])
            elif "OUTRAS DESPESAS VARIÁVEIS" in nome and "PESSOAL" in nome:
                valores["outras_desp"] += limpar(linha[5])
            elif "OUTRAS DESPESAS DE PESSOAL DECORRENTES" in nome:
                valores["terceirizacao"] += limpar(linha[5])
            elif "SENTENÇAS JUDICIAIS" in nome and "TRABALHISTAS" in nome:
                valores["sentencas_trabalhistas"] += limpar(linha[5])
        return valores
    
    dados_atual = extrair_bo(caminho_atual)
    dados_anteriores = [extrair_bo(c) for c in caminhos_anteriores]
    
    custo_atual = dados_atual["pessoal"] + dados_atual["outras_desp"] + dados_atual["terceirizacao"] - dados_atual["sentencas_trabalhistas"]
    rcl_atual = dados_atual["receitas_correntes"]
    
    custo_anterior = 0.0
    rcl_anterior = 0.0
    for d in dados_anteriores:
        custo_anterior += d["pessoal"] + d["outras_desp"] + d["terceirizacao"] - d["sentencas_trabalhistas"]
        rcl_anterior += d["receitas_correntes"]
    
    return {
        "erro": False,
        "rcl_atual": rcl_atual, "rcl_anterior": rcl_anterior, "rcl_total": rcl_atual + rcl_anterior,
        "pessoal_atual": dados_atual["pessoal"], "pessoal_anterior": sum(d["pessoal"] for d in dados_anteriores),
        "pessoal_total": dados_atual["pessoal"] + sum(d["pessoal"] for d in dados_anteriores),
        "outras_atual": dados_atual["outras_desp"], "outras_anterior": sum(d["outras_desp"] for d in dados_anteriores),
        "outras_total": dados_atual["outras_desp"] + sum(d["outras_desp"] for d in dados_anteriores),
        "terc_atual": dados_atual["terceirizacao"], "terc_anterior": sum(d["terceirizacao"] for d in dados_anteriores),
        "terc_total": dados_atual["terceirizacao"] + sum(d["terceirizacao"] for d in dados_anteriores),
        "custo_atual": custo_atual, "custo_anterior": custo_anterior, "custo_total": custo_atual + custo_anterior
    }
















@app.get("/api/custo_pessoal/{periodo}")
async def api_custo_pessoal(periodo: str):
    from matriz_integridade import _get_csv, _ler_linhas, _limpar_valor
    import re, os
    
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
            if "OUTRAS DESPESAS VARIÁVEIS" in nome and "PESSOAL" in nome:
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
        "custo_anterior": custo_anterior,
        "custo_total": custo_atual + custo_anterior
    }


@app.get("/salvar_custo_pessoal/{periodo}")
async def salvar_custo_pessoal(periodo: str):
    try:
        # Chama a API para pegar os dados calculados
        dados = await api_custo_pessoal(periodo)
        if dados.get("erro"):
            raise HTTPException(status_code=400, detail="Dados faltando")
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_custo_pessoal (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_custo_pessoal (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", 
                       (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"mensagem": "Salvo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historico_custo_pessoal")
async def listar_historico_custo_pessoal():
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













@app.get("/api/diag_custo_pessoal")
async def diag_custo_pessoal(periodo: str = "2026-TRIMESTRE-3"):
    from playwright.async_api import async_playwright
    from fastapi.responses import Response
    import tempfile, os
    
    url = f"http://127.0.0.1:8000/analise_custo_pessoal?autoprint=1&periodo={periodo}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Tira um screenshot ANTES de qualquer remoção
        screenshot_bytes = await page.wait_for_timeout(2500)
        await page.pdf(full_page=True)
        await browser.close()
        
        return Response(content=screenshot_bytes, media_type="image/png", headers={
            "Content-Disposition": "inline; filename=diag.png"
        })





@app.get("/gerar_pdf_custo_pessoal")
async def gerar_pdf_custo_pessoal(periodo: str = "2026-TRIMESTRE-3"):
    try:
        from playwright.async_api import async_playwright
        from fastapi.responses import Response
        
        url = f"http://127.0.0.1:8000/analise_custo_pessoal?autoprint=1&periodo={periodo}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.emulate_media(media="print")
            await page.goto(url, wait_until="networkidle")
            
            # Espera o conteúdo principal carregar (ex: o título "Fundamentação Legal")
            try:
                await page.wait_for_selector("text=Fundamentação Legal", timeout=10000)
            except:
                pass  # se não achar, segue mesmo assim
            await page.wait_for_timeout(2000)
            
            # Esconde a sidebar pelo seletor estrutural: a div que contém o flex layout
            # Vamos esconder a PRIMEIRA div filha do container flex (que é a sidebar)
            await page.evaluate("""
                () => {
                    // Procura o container flex principal
                    const flexContainer = document.querySelector('div[style*="display: flex"]');
                    if (flexContainer && flexContainer.children.length >= 2) {
                        // Esconde o primeiro filho (sidebar) e mantém o segundo (conteúdo)
                        flexContainer.children[0].style.display = 'none';
                    }
                    // Esconde botões e top-bar
                    document.querySelectorAll('.btn, .btn-verificar, .btn-salvar, .top-bar').forEach(el => el.style.display = 'none');
                    document.body.style.background = 'white';
                }
            """)
            await page.wait_for_timeout(500)
            
            pdf_bytes = await page.emulate_media(media="print")
        await page.wait_for_timeout(2500)
        await page.emulate_media(media="print")
        await page.wait_for_timeout(2000)
        await page.pdf(path=pdf_path, format="A4", print_background=True, margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"})
        await browser.close()
            
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=custo_pessoal_{periodo}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        for p in l_bp:
            if len(p) > coluna:
                for celula in p:
                    if termo.upper() in str(celula).upper():
                        return abs(_limpar_valor(p[coluna]))
        return 0.0

    # --- BUSCA DOS VALORES EXATOS DO BP ---
    ativo_circulante = buscar("ATIVO CIRCULANTE", 1)
    caixa = buscar("CAIXA E EQUIVALENTES", 1)
    estoques = buscar("ESTOQUES", 1) or buscar("ESTOQUES", 3)
    realizavel = buscar("ATIVO REALIZÁVEL A LONGO PRAZO", 1)
    passivo_circulante = buscar("PASSIVO CIRCULANTE", 3) or buscar("ATIVO CIRCULANTE", 3)
    passivo_nao_circulante = buscar("PASSIVO NAO-CIRCULANTE", 3) or buscar("PASSIVO NÃO CIRCULANTE", 3)
    
    # Variáveis exatas do BP
    ativo_permanente = buscar("ATIVO PERMANENTE", 1)
    patrimonio_liquido = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 3)

    # --- CÁLCULO DA LIQUIDEZ ---
    liq_imediata = (caixa / passivo_circulante) if passivo_circulante > 0 else 0
    liq_corrente = (ativo_circulante / passivo_circulante) if passivo_circulante > 0 else 0
    liq_seca = ((ativo_circulante - estoques) / passivo_circulante) if passivo_circulante > 0 else 0
    denom_geral = passivo_circulante + passivo_nao_circulante
    liq_geral = ((ativo_circulante + realizavel) / denom_geral) if denom_geral > 0 else 0

    # --- CÁLCULO DA ESTRUTURA (BUSCA EXATA NO BP) ---
    # Busca os totais exatos que já existem no BP
    ativo_total = buscar("ATIVO NÃO CIRCULANTE", 1) + ativo_circulante or buscar("TOTAL DO ATIVO", 1) or (ativo_circulante + realizavel + ativo_permanente)
    passivo_total = buscar("TOTAL DO PASSIVO", 3) or (passivo_circulante + passivo_nao_circulante)
    
    endividamento_geral = round((passivo_total / ativo_total) * 100, 2) if ativo_total > 0 else 0
    part_capital_terceiros = round((passivo_total / patrimonio_liquido) * 100, 2) if patrimonio_liquido > 0 else 0
    imobilizacao_pl = round((ativo_permanente / patrimonio_liquido) * 100, 2) if patrimonio_liquido > 0 else 0

    return {
        "liquidez": {
            "liquidez_imediata": round(liq_imediata, 2),
            "liquidez_corrente": round(liq_corrente, 2),
            "liquidez_seca": round(liq_seca, 2),
            "liquidez_geral": round(liq_geral, 2)
        },
        "estrutura": {
            "endividamento_geral": endividamento_geral,
            "part_capital_terceiros": part_capital_terceiros,
            "imobilizacao_pl": imobilizacao_pl
        },
        "valores": {
            "ativo_circulante": ativo_circulante,
            "passivo_circulante": passivo_circulante,
            "caixa": caixa,
            "estoques": estoques,
            "realizavel": realizavel,
            "passivo_nao_circulante": passivo_nao_circulante,
            "ativo_total": ativo_total,
            "passivo_total": passivo_total,
            "patrimonio_liquido": patrimonio_liquido,
            "ativo_permanente": ativo_permanente
        }
    }

@app.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str):
    # === REGRA DE INTEGRIDADE ===
    from matriz_integridade import _get_csv
    if not _get_csv("BALANCO_PATRIMONIAL", periodo):
        return {"erro": "faltando", "pecas": ["Balanço Patrimonial"]}
    dados = _calc_liquidez(periodo)
    if not dados:
        return {"erro": "faltando", "pecas": ["Balanço Patrimonial"]}
    return dados

@app.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historico_liquidez WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return {"mensagem": "Excluido"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez(periodo: str):
    dados = _calc_liquidez(periodo)
    if not dados: raise HTTPException(status_code=404, detail="Arquivo nao encontrado")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", 
                   (periodo, data_agora, json.dumps(dados)))
    conn.commit()
    conn.close()
    return {"mensagem": "Liquidez salva!", "dados": dados}

@app.get("/historico_liquidez")
async def listar_liquidez():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_liquidez ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_liquidez/{id}")
async def get_historico_liquidez(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    
    periodo, json_str = row
    dados = json.loads(json_str)
    
    # Se os dados antigos nao tem estrutura, recalcula
    if "estrutura" not in dados:
        novos_dados = _calc_liquidez(periodo)
        if novos_dados:
            dados = novos_dados
    
    return dados


@app.get("/gerar_pdf_liquidez/{id}")
async def gerar_pdf_liquidez(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
        
        periodo, data_geracao, json_str = row
        dados = json.loads(json_str)
        
        # Garante que os dados de estrutura existam (mesmo em históricos antigos)
        if "estrutura" not in dados:
            novos_dados = _calc_liquidez(periodo)
            if novos_dados:
                dados = novos_dados
        
        res = dados["liquidez"]
        est = dados.get("estrutura", {})
        val = dados["valores"]

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 18)
        pdf.set_text_color(0, 86, 179)
        pdf.cell(0, 10, "Indices de Liquidez", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "", 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Período: {periodo} | Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)

        def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def desenhar_card(titulo, valor, formula):
            # Se o Y atual + 45mm (tamanho do card + margem) passar do limite da página (A4 = 297mm - 20mm de margem)
            if pdf.get_y() + 45 > 277:
                pdf.add_page()
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, "Indices de Liquidez (Continuacao)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(5)
            
            pdf.set_fill_color(248, 251, 255)
            pdf.rect(15, pdf.get_y(), 180, 35, style='F')
            pdf.set_fill_color(0, 86, 179)
            pdf.rect(15, pdf.get_y(), 180, 2, style='F')
            pdf.set_xy(20, pdf.get_y() + 5)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 6, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_x(20)
            pdf.set_font("helvetica", "B", 20)
            pdf.set_text_color(0, 86, 179)
            pdf.cell(0, 10, str(valor), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_x(20)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(170, 5, formula, border=1)
            pdf.ln(10)

        desenhar_card("Liquidez Imediata", res["liquidez_imediata"], f"(Caixa) / (Passivo Circulante) | ({fmt(val['caixa'])}) / ({fmt(val['passivo_circulante'])})")
        desenhar_card("Liquidez Corrente", res["liquidez_corrente"], f"(Ativo Circulante) / (Passivo Circulante) | ({fmt(val['ativo_circulante'])}) / ({fmt(val['passivo_circulante'])})")
        desenhar_card("Liquidez Seca", res["liquidez_seca"], f"((Ativo Circulante - Estoques)) / (Passivo Circulante) | (({fmt(val['ativo_circulante'])} - {fmt(val['estoques'])})) / ({fmt(val['passivo_circulante'])})")
        desenhar_card("Liquidez Geral", res["liquidez_geral"], f"(Ativo Circulante + Realizável a Longo Prazo) / (Passivo Circulante + Passivo Não Circulante) | ({fmt(val['ativo_circulante'])} + {fmt(val['realizavel'])}) / ({fmt(val['passivo_circulante'])} + {fmt(val['passivo_nao_circulante'])})")

        # --- CALCULO ESTRUTURA (MESMA LOGICA DO FRONTEND) ---
        v_ativa_circ = val.get('ativo_circulante', 0)
        v_realizavel = val.get('realizavel', 0)
        v_ativo_perm = val.get('ativo_permanente', 0)
        v_passivo_circ = val.get('passivo_circulante', 0)
        v_passivo_nao_circ = val.get('passivo_nao_circulante', 0)
        v_pl = val.get('patrimonio_liquido', 0)
        
        ativo_total = val.get('ativo_total', 0) or (v_ativa_circ + v_ativo_perm)
        passivo_total = val.get('passivo_total', 0) or (v_passivo_circ + v_passivo_nao_circ)
        
        endividamento = (passivo_total / ativo_total * 100) if ativo_total > 0 else 0
        part_capital = (passivo_total / v_pl * 100) if v_pl > 0 else 0
        imobilizacao = (v_ativo_perm / v_pl * 100) if v_pl > 0 else 0

        # Formatação dos valores (para moeda)
        f_ativo_total = fmt(ativo_total)
        f_passivo_total = fmt(passivo_total)
        f_pl = fmt(v_pl)
        f_ativo_perm = fmt(v_ativo_perm)

        # Desenha os 3 novos cards no PDF
        desenhar_card("Endividamento Geral", f"{endividamento:.2f}%", f"Passivo Total / Ativo Total | ({f_passivo_total}) / ({f_ativo_total})")
        desenhar_card("Part. de Capital de Terceiros", f"{part_capital:.2f}%", f"Passivo / PL | ({f_passivo_total}) / ({f_pl})")
        desenhar_card("Imobilização do PL", f"{imobilizacao:.2f}%", f"Ativo Perm. / PL | ({f_ativo_perm}) / ({f_pl})")


        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Indices_{periodo.replace('-', '_')}.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




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
        html += "<h2>Analises de Integridade - " + periodo + "</h2>"
        
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







if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
