from pathlib import Path

arquivo = Path("pc_frontend/analise_dvp.html")
conteudo = arquivo.read_text(encoding="utf-8")

print("=== Botões e funções no analise_dvp.html ===")
for i, linha in enumerate(conteudo.split("\n"), 1):
    if any(t in linha for t in ["Verificar", "Exibir", "verificar", "exibir", "onclick", "fetch"]):
        print(f"{i:>4}: {linha.strip()[:120]}")
