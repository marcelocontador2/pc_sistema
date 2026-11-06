import os
import glob

folder = r"pc_backend"
arquivos = glob.glob(os.path.join(folder, "**", "*.py"), recursive=True)

with open("onde_esta_o_pdf.txt", "w", encoding="utf-8") as out:
    for arq in arquivos:
        with open(arq, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
        for i, linha in enumerate(linhas):
            if "ANALISE DO BALANCO PATRIMONIAL" in linha.upper() or "COFEN/BR" in linha.upper():
                out.write(f"Arquivo: {arq} (Linha {i+1})\n")
                # Pega as 10 linhas antes para ver o nome da função
                inicio = max(0, i - 15)
                for j in range(inicio, i + 5):
                    out.write(f"  {linhas[j]}")
                out.write("\n" + "="*50 + "\n")

print("[OK] Busca concluída! Abrindo o arquivo 'onde_esta_o_pdf.txt'...")
