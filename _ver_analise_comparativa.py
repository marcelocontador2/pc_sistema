from pathlib import Path

arquivo_path = "pc_backend/app/analytics/analise_comparativa.py"
conteudo = Path(arquivo_path).read_text(encoding="utf-8")

print(f"ARQUIVO: {arquivo_path}")
print(f"Linhas: {len(conteudo.split(chr(10)))}")
print("=" * 80)
for i, linha in enumerate(conteudo.split("\n"), 1):
    print(f"{i:>4}: {linha}")
