import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Corrige a linha 7075 (index 7074)
alvo = 7074
if alvo < len(linhas):
    print(f"Linha original {alvo+1}: {linhas[alvo].rstrip()}")
    # Substitui a linha inteira pelo append correto
    linhas[alvo] = '                        html_parts.append("</tbody></table>")\n'
    print(f"Linha corrigida {alvo+1}: {linhas[alvo].rstrip()}")
else:
    print("[ERRO] Linha 7075 nao encontrada (arquivo menor).")

# Salva
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo salvo.")
