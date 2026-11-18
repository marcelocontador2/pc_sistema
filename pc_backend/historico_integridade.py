from fastapi import APIRouter

# Router vazio para satisfazer a importacao do main.py
router = APIRouter()

@router.get("/historico_integridade")
async def get_historico_integridade():
    return {"mensagem": "Historico de integridade (rota temporaria)"}

@router.get("/historico_integridade/{id}")
async def get_historico_integridade_id(id: int):
    return {"id": id, "mensagem": "Detalhe do historico (rota temporaria)"}
