from pathlib import Path

for arquivo_path in ["pc_backend/app/analytics/analise_completa.py", "pc_backend/app/analytics/analise_resultados.py"]:
    print(f"\n{'='*80}")
    print(f"ARQUIVO: {arquivo_path}")
    print(f"{'='*80}")
    conteudo = Path(arquivo_path).read_text(encoding="utf-8")
    for i, linha in enumerate(conteudo.split("\n"), 1):
        print(f"{i:>4}: {linha}")
