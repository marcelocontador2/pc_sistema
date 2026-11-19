from pathlib import Path
import importlib
import os
import sys

from fastapi import HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

_RAIZ = Path(__file__).resolve().parent.parent
_FRONTEND_DIR = _RAIZ / "pc_frontend"

if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

app = FastAPI(title="PC - Prestacao de Contas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTERS = [
    "pc_backend.app.routers.analise_financeira",
    "pc_backend.app.routers.analise_orcamentaria",
    "pc_backend.app.routers.balanco_financeiro",
    "pc_backend.app.routers.bp",
    "pc_backend.app.routers.conferencia",
    "pc_backend.app.routers.despesas",
    "pc_backend.app.routers.dfc",
    "pc_backend.app.routers.dmpl",
    "pc_backend.app.routers.dvp",
    "pc_backend.app.routers.integridade",
    "pc_backend.app.routers.liquidez",
    "pc_backend.app.routers.panorama",
    "pc_backend.app.routers.receitas",
    "pc_backend.app.routers.relatorio_consolidado",
    "pc_backend.app.routers.notas_itens",
]

for mod_name in ROUTERS:
    modulo = importlib.import_module(mod_name)
    if hasattr(modulo, "router"):
        app.include_router(modulo.router)

if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_file = _FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>PC - Prestacao de Contas API</h1><p>Backend modular ativo.</p>")


@app.get("/relatorio_consolidado", response_class=HTMLResponse)
@app.get("/relatorio_consolidado.html", response_class=HTMLResponse)
async def rota_relatorio_consolidado():
    base_front = globals().get("_FRONTEND_DIR") or Path("pc_frontend")
    arq = Path(base_front) / "relatorio_consolidado.html"
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="relatorio_consolidado.html nao encontrado")
