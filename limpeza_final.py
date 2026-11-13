import shutil

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

shutil.copy(caminho, caminho + ".bak_limpeza_final")

# Mostra o que será removido (linhas 4563 a 4569, índices 4562 a 4568)
print("🗑️ Removendo as seguintes linhas:")
for i in range(4562, 4569):
    if i < len(linhas):
        print(f"   {i+1:5d}: {linhas[i]}", end="")

# Remove do maior índice para o menor para não bagunçar os índices
for i in range(4568, 4561, -1):
    if i < len(linhas):
        del linhas[i]

with open(caminho, "w", encoding="utf-8") as f:
    f.writelines(linhas)

print("\n✅ Linhas removidas.")

# Verifica a sintaxe
try:
    with open(caminho, "r", encoding="utf-8") as f:
        compile(f.read(), caminho, "exec")
    print("✅ Arquivo main.py está sintaticamente válido!")
except SyntaxError as e:
    print(f"\n❌ Ainda há erro na linha {e.lineno}: {e.msg}")
    print(f"   Texto: {e.text}")
    # Mostra o contexto do novo erro
    with open(caminho, "r", encoding="utf-8") as f:
        linhas_atuais = f.readlines()
    inicio = max(0, e.lineno - 5)
    fim = min(len(linhas_atuais), e.lineno + 5)
    print("\n📋 Contexto do erro:")
    for i in range(inicio, fim):
        marcador = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marcador} {i+1:5d}: {linhas_atuais[i]}", end="")
