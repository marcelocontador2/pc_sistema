from fastapi import APIRouter

router = APIRouter()

@router.get("/integridade")
async def get_integridade():
    return {"mensagem": "Rota de integridade (temporaria)"}

@router.get("/integridade/{id}")
async def get_integridade_id(id: int):
    return {"id": id, "mensagem": "Detalhe de integridade (temporaria)"}
