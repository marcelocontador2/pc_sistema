from pathlib import Path
import shutil

arquivo = Path("pc_backend/main.py")
backup = Path("pc_backend/main.py.bak_antes_remover_comentarios_removidos")
shutil.copy2(arquivo, backup)
print(f"Backup criado: {backup}")

conteudo = arquivo.read_text(encoding="utf-8")
linhas = conteudo.split("\n")

# Remover linhas que contenham "[REMOVIDO" (comentarios de refatoracoes anteriores)
novas_linhas = []
removidas = 0
for linha in linhas:
    if "[REMOVIDO" in linha:
        removidas += 1
        continue
    novas_linhas.append(linha)

conteudo_novo = "\n".join(novas_linhas)
arquivo.write_text(conteudo_novo, encoding="utf-8")

print(f"Linhas removidas: {removidas}")
print(f"Tamanho antes: {len(conteudo)} chars")
print(f"Tamanho depois: {len(conteudo_novo)} chars")

# Compilar
import py_compile
try:
    py_compile.compile(str(arquivo), doraise=True)
    print("OK: main.py compila apos remocao")
except Exception as e:
    print(f"ERRO: NAO compila: {e}")
    print("Restaurando do backup...")
    shutil.copy2(backup, arquivo)
    print("Backup restaurado.")
