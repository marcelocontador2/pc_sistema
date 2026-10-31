from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Garantir que o carregarHistorico esta no onload
if "carregarHistorico()" not in conteudo:
    # Procurar o window.onload
    match = re.search(r"(window\.onload\s*=\s*function\s*\(\)\s*\{[^}]*carregar\(\);)", conteudo)
    if match:
        trecho = match.group(1)
        novo_trecho = trecho.replace("carregar();", "carregar(); carregarHistorico();")
        conteudo = conteudo.replace(trecho, novo_trecho, 1)
        print("OK: carregarHistorico adicionado no onload!")
    else:
        print("AVISO: nao achei o window.onload com carregar()")
else:
    print("OK: carregarHistorico ja existe no onload")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: Historico corrigido!")
