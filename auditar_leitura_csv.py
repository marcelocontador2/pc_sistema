import os, re

print("=" * 70)
print("AUDITORIA: ONDE OS CSVs DE BF E DFC SÃO LIDOS")
print("=" * 70)

# 1. Procura em todos os .py do projeto (fora venv/backup) por "open(" com csv
pastas_ignorar = {"pc_venv", "__pycache__", ".git", "_backups_arquivo", "_arquivo_20261031"}
arquivos_alvo = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in pastas_ignorar]
    for nome in files:
        if nome.endswith(".py"):
            caminho = os.path.join(root, nome)
            try:
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                    if "open(" in txt and (".csv" in txt or "csv" in txt.lower()):
                        if "balanco_financeiro" in caminho.lower() or "dfc" in caminho.lower() or "balanco_financeiro" in txt.lower() or "processar_bf" in txt.lower() or "processar_dfc" in txt.lower():
                            arquivos_alvo.append(caminho)
            except Exception:
                pass

print("\nArquivos candidatos (leitura de CSV):")
for a in arquivos_alvo:
    print(f"  {a}")

# 2. Mostra trechos de "open(" com encoding em cada arquivo candidato
for caminho in arquivos_alvo:
    print(f"\n{'='*70}")
    print(f"ARQUIVO: {caminho}")
    print('='*70)
    
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    
    for m in re.finditer(r'open\([^)]*\)', txt):
        trecho = m.group(0)
        if ".csv" in trecho.lower() or "encoding" in trecho.lower() or "latin" in trecho.lower():
            linha = txt[:m.start()].count("\n") + 1
            print(f"  Linha {linha}: {trecho}")
