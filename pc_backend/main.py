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
    "pc_backend.app.routers.notas_explicativas",
    "pc_backend.app.routers.configuracoes",
    "pc_backend.app.routers.compat_rotas",
    "pc_backend.app.routers.importacao",
    "pc_backend.app.routers.usuarios",
]

for mod_name in ROUTERS:
    modulo = importlib.import_module(mod_name)
    if hasattr(modulo, "router"):
        app.include_router(modulo.router)

if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")

from fastapi import HTTPException
from fastapi.responses import FileResponse

@app.get("/js/{caminho_js:path}")
def servir_js_frontend(caminho_js: str):
    if ".." in caminho_js or caminho_js.startswith(("/", "\\")):
        raise HTTPException(status_code=400, detail="Caminho inv?lido.")
    arq = (_FRONTEND_DIR / "js" / caminho_js).resolve()
    base_js = (_FRONTEND_DIR / "js").resolve()
    if not str(arq).startswith(str(base_js)) or not arq.exists() or not arq.is_file():
        raise HTTPException(status_code=404, detail="Arquivo JS n?o encontrado.")
    return FileResponse(str(arq), media_type="application/javascript; charset=utf-8", headers={"Cache-Control": "no-cache"})

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


@app.get("/notas_explicativas", response_class=HTMLResponse)
@app.get("/notas_explicativas.html", response_class=HTMLResponse)
async def rota_notas_explicativas():
    base_front = globals().get("_FRONTEND_DIR") or Path("pc_frontend")
    arq = Path(base_front) / "notas_explicativas.html"
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="notas_explicativas.html nao encontrado")
