import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_fix_valores_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Substitui TODAS as ocorrências de fmtMi no bloco de grupos por fmt
# (Apenas no trecho do htmlGrupos)
inicio = c.find('let htmlGrupos')
fim = c.find('document.getElementById(\'lista-grupos\').innerHTML', inicio)

if inicio == -1 or fim == -1:
    print("[ERRO] Não encontrei o bloco htmlGrupos.")
    exit(1)

bloco = c[inicio:fim]
print("--- BLOCO ATUAL (original) ---")
print(bloco[:1500])

# Faz as substituições no bloco
novo_bloco = bloco.replace('fmtMi(', 'fmt(')
# Corrige a formatação do texto para incluir o "R$ "
novo_bloco = novo_bloco.replace("'R$ ' + fmt(", "'R$ ' + fmt(")  # já está correto se fmt formata assim

# 2. Substitui o bloco no arquivo
c = c[:inicio] + novo_bloco + c[fim:]

open(arquivo, 'w', encoding='utf-8').write(c)
print("\n[OK] Bloco de grupos atualizado (fmtMi -> fmt).")
print("\n--- BLOCO NOVO ---")
print(novo_bloco[:1500])
