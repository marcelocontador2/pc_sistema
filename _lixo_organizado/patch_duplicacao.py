import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Remove a linha duplicada do faltando.append dentro do except
linhas = texto.splitlines(keepends=True)

# Procura a duplicação: duas linhas seguidas iguais dentro do except
encontrou = False
for i in range(len(linhas) - 1):
    if 'faltando.append({"nome": nomes_amigaveis.get(chave, chave)})' in linhas[i] and \
       'faltando.append({"nome": nomes_amigaveis.get(chave, chave)})' in linhas[i+1] and \
       'except Exception as e:' in linhas[i-1]:
        # Remove a segunda ocorrência
        linhas[i+1] = ''
        encontrou = True
        print(f"[OK] Duplicação removida nas linhas {i+1} e {i+2}.")
        break

if not encontrou:
    print("[AVISO] Não encontrei a duplicação. Pode já ter sido removida.")

arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo salvo.")
