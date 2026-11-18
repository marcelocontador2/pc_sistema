from pathlib import Path
import shutil

arquivo = Path("pc_backend/main.py")
backup = Path("pc_backend/main.py.bak_antes_descomentar_routers")
shutil.copy2(arquivo, backup)
print(f"Backup criado: {backup}")

conteudo = arquivo.read_text(encoding="utf-8")

# 1. Descomentar panorama (com prefixo pc_backend)
antigo_panorama = """# [REMOVIDO - import quebrado] from app.routers.panorama import router as panorama_router
# [REMOVIDO - dependente de import quebrado] app.include_router(panorama_router)"""

novo_panorama = """from pc_backend.app.routers.panorama import router as panorama_router
app.include_router(panorama_router)"""

if antigo_panorama in conteudo:
    conteudo = conteudo.replace(antigo_panorama, novo_panorama, 1)
    print("  OK: panorama_router descomentado (com prefixo pc_backend)")
else:
    print("  AVISO: bloco do panorama nao encontrado (pode ja estar correto)")

# 2. Descomentar balanco_financeiro (com prefixo pc_backend)
antigo_bf = """# [REMOVIDO - import quebrado] from app.routers.balanco_financeiro import router as bf_router
# [REMOVIDO - dependente de import quebrado] app.include_router(bf_router)"""

novo_bf = """from pc_backend.app.routers.balanco_financeiro import router as bf_router
app.include_router(bf_router)"""

if antigo_bf in conteudo:
    conteudo = conteudo.replace(antigo_bf, novo_bf, 1)
    print("  OK: bf_router descomentado (com prefixo pc_backend)")
else:
    print("  AVISO: bloco do BF nao encontrado (pode ja estar correto)")

# 3. Remover duplicata comentada do dvp (ja registrado na linha 987)
antigo_dvp = """# [REMOVIDO - import quebrado] from app.routers.dvp import router as dvp_router
# [REMOVIDO - dependente de import quebrado] app.include_router(dvp_router)"""

if antigo_dvp in conteudo:
    conteudo = conteudo.replace(antigo_dvp, "# dvp.router ja registrado na linha 987", 1)
    print("  OK: duplicata comentada do dvp removida")
else:
    print("  AVISO: bloco do dvp nao encontrado")

arquivo.write_text(conteudo, encoding="utf-8")

# 4. Compilar
import py_compile
try:
    py_compile.compile(str(arquivo), doraise=True)
    print("OK: main.py compila apos descomentar routers")
except Exception as e:
    print(f"ERRO: NAO compila: {e}")
    print("Restaurando do backup...")
    shutil.copy2(backup, arquivo)
    print("Backup restaurado.")
