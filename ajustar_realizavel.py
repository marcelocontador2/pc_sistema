import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_realizavel_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Adiciona a linha do Ativo Realizavel apos o Ativo Nao Circulante
antigo = """html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);"""

novo = """html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Ativo Realizável a Longo Prazo', d.ativo_realizavel.atual, d.ativo_realizavel.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Linha 'Ativo Realizável a Longo Prazo' adicionada na tabela.")
else:
    print("[AVISO] Trecho do render nao encontrado.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend ajustado.")
