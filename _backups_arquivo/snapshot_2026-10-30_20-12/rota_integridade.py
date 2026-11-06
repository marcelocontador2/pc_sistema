from fastapi import APIRouter, HTTPException
import sqlite3, json, datetime, os
router = APIRouter()
@router.get("/salvar_integridade/{periodo}")
async def salvar_integridade(periodo: str):
    try:
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        json_resultado = json.dumps(dados)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historico_integridade (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", (periodo, data_agora, json_resultado))
        conn.commit()
        conn.close()
        return {"mensagem": "Integridade salva!", "dados": dados}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
