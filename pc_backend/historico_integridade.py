import sqlite3
import re
import json
import datetime
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

# Caminho do banco de dados SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")

# Cria a tabela no banco assim que o modulo for carregado
def criar_tabela():
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

criar_tabela()


@router.get("/salvar_integridade/{periodo}")
async def salvar_integridade(periodo: str):
    try:
        # 1. VALIDAÇÃO: Verifica se todos os arquivos obrigatórios existem
        import os, glob
        pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
        pecas_faltando = []
        
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        p_limpo = re.sub(r'[^A-Z0-9]', '_', str(periodo).upper()).strip('_')
        
        for peca in pecas_obrigatorias:
            nome_arquivo = f"{peca}_{p_limpo}.csv"
            if not os.path.exists(os.path.join(pasta, nome_arquivo)):
                pecas_faltando.append(peca)
                
        if pecas_faltando:
            return {"erro": "faltando", "pecas": pecas_faltando}

        # 2. Se passou, calcula e salva
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        
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
        
        return {"mensagem": "Integridade salva com sucesso!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
    
    if not row:
        raise HTTPException(status_code=404, detail="Historico nao encontrado")
        
    return json.loads(row[0])

@router.delete("/excluir_integridade/{id}")
async def excluir_historico(id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM historico_integridade WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return {"mensagem": "Historico excluido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
