arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

with open("trecho_cabecalho_bp.txt", "w", encoding="utf-8") as out:
    # Pega as 40 linhas antes da função 'def linha' para achar o cabeçalho e o col_w
    for i in range(5400, 5470):
        if i < len(linhas):
            out.write(f"{i+1}: {linhas[i]}")

print("[OK] Cabeçalho extraído para 'trecho_cabecalho_bp.txt'")
