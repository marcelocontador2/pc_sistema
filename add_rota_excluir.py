import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_rota_excluir_{ts}")

c = open(back_path, encoding="utf-8-sig").read()
linhas = c.split("\n")

# Encontra a linha que define UPLOAD_DIR (linha 217)
idx_alvo = -1
for i, ln in enumerate(linhas):
    if "UPLOAD_DIR" in ln and "=" in ln and "os.path.join" in ln:
        idx_alvo = i
        break

if idx_alvo == -1:
    print("[ERRO] Nao encontrei a definicao de UPLOAD_DIR no main.py.")
    exit(1)

print(f"[INFO] UPLOAD_DIR encontrado na linha {idx_alvo+1}: {linhas[idx_alvo].strip()}")

# Detecta a indentacao (geralmente 0 para rotas top-level)
indent = ""
if linhas[idx_alvo].startswith(" "):
    indent = " " * (len(linhas[idx_alvo]) - len(linhas[idx_alvo].lstrip()))

# Monta a rota (ASCII puro, sem acentos no codigo)
rota = [
    "",
    "",
    "# === ROTA: Excluir relatorio CSV da pasta uploads_raw ===",
    "@app.delete(\"/api/excluir_relatorio/{nome_arquivo}\")",
    "async def excluir_relatorio_csv(nome_arquivo: str):",
    "    # Seguranca: impede path traversal",
    "    if '..' in nome_arquivo or '/' in nome_arquivo or '\\\\' in nome_arquivo:",
    "        raise HTTPException(status_code=400, detail=\"Nome de arquivo invalido.\")",
    "    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)",
    "    if not os.path.exists(caminho):",
    "        raise HTTPException(status_code=404, detail=\"Arquivo nao encontrado: \" + nome_arquivo)",
    "    try:",
    "        os.remove(caminho)",
    "        return {\"ok\": True, \"mensagem\": \"Arquivo excluido: \" + nome_arquivo}",
    "    except Exception as e:",
    "        raise HTTPException(status_code=500, detail=\"Erro ao excluir: \" + str(e))",
    "",
]

# Insere depois da linha do UPLOAD_DIR
linhas_novas = linhas[:idx_alvo+1] + rota + linhas[idx_alvo+1:]
c_novo = "\n".join(linhas_novas)
open(back_path, "w", encoding="utf-8").write(c_novo)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
    print(f"[OK] Rota inserida apos a linha {idx_alvo+1}.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_rota_excluir_{ts}", back_path)
    print("[OK] Backup restaurado.")
