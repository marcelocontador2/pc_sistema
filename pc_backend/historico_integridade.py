import sqlite3
import re
import json
import datetime
from fastapi import APIRouter, HTTPException, Body, Body, Body, Body, Body
from fastapi.responses import Response
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")

def criar_tabelas():
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_matriz_integridade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periodo TEXT NOT NULL,
            data_geracao TEXT NOT NULL,
            resultado_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

criar_tabelas()

# ==========================================
# ROTAS DA CONFERÊNCIA (MANTIDAS ORIGINAIS)
# ==========================================

@router.get("/historico_integridade")
async def listar_historico():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT id, periodo, data_geracao FROM historico_integridade ORDER BY id DESC''')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@router.get("/historico_integridade/{id}")
async def buscar_historico(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT resultado_json FROM historico_integridade WHERE id = ?''', (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
    return json.loads(row[0])

@router.delete("/excluir_integridade/{id}")
async def excluir_historico(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM historico_integridade WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Historico excluido com sucesso!"}

@router.get("/salvar_integridade_cruzada/{periodo}")
async def salvar_integridade_cruzada(periodo: str):
    return await salvar_integridade(periodo)

# ==========================================
# ROTAS DA MATRIZ (NOVA TABELA SEPARADA)
# ==========================================
@router.post("/salvar_matriz_historico/{periodo}")
async def salvar_matriz_historico(periodo: str, payload: dict = Body(None)):
    try:
        from matriz_integridade import gerar_matriz
        dados = await gerar_matriz(periodo)
        
        if isinstance(dados, dict) and dados.get("erro") == "faltando": 
            return dados
            
        if payload and "campos_editados" in payload:
            for linha in dados.get("matriz", []):
                if linha.get("is_editable"):
                    item = linha.get("item")
                    linha["balancete"] = payload["campos_editados"].get(f"edit_bal_{item}", linha["balancete"])
                    linha["bo"] = payload["campos_editados"].get(f"edit_bo_{item}", linha["bo"])
                    linha["dvp"] = payload["campos_editados"].get(f"edit_dvp_{item}", linha["dvp"])

        if payload and "justificativas" in payload:
            justificativas = payload["justificativas"]
            for linha in dados.get("matriz", []):
                conf = str(linha.get("conf", ""))
                if conf in justificativas and justificativas[conf].strip() != "":
                    linha["observacao"] = justificativas[conf]
                    
        # Injeta as justificativas no JSON se existirem
        if payload and "justificativas" in payload:
            for linha in dados.get("matriz", []):
                conf = str(linha.get("conf", ""))
                if conf in payload["justificativas"] and payload["justificativas"][conf].strip() != "":
                    linha["observacao"] = payload["justificativas"][conf]

        json_resultado = json.dumps(dados)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historico_matriz_integridade (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", (periodo, data_agora, json_resultado))
        conn.commit()
        conn.close()
        
        return {"mensagem": "Sucesso", "dados": dados}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/historico_matriz")
async def listar_historico_matriz():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT id, periodo, data_geracao FROM historico_matriz_integridade ORDER BY id DESC''')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@router.get("/historico_matriz/{id}")
async def buscar_historico_matriz(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT resultado_json FROM historico_matriz_integridade WHERE id = ?''', (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
    return json.loads(row[0])

@router.delete("/excluir_matriz/{id}")
async def excluir_historico_matriz(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM historico_matriz_integridade WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Historico excluido!"}

