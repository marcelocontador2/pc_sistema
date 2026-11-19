import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Corrige a linha 8740 (index 8739)
alvo = 8739
if alvo < len(linhas):
    print("Linha original:", repr(linhas[alvo]))
    # Remove os 8 espacos extras (deixa 4 espacos)
    linhas[alvo] = '    encontrados = []\n'
    print("Linha corrigida:", repr(linhas[alvo]))

# Tambem corrige os mojibakes nos nomes amigaveis (linhas 8732-8737)
for i in range(8725, min(8740, len(linhas))):
    linhas[i] = linhas[i].replace("ÃÂndices de Liquidez", "Índices de Liquidez")
    linhas[i] = linhas[i].replace("Integridade entre DemonstraÃ§Ãµes", "Integridade entre Demonstrações")
    linhas[i] = linhas[i].replace("ConferÃªncia das DemonstraÃ§Ãµes", "Conferência das Demonstrações")
    linhas[i] = linhas[i].replace("AnÃ¡lise por Centro de Custos", "Análise por Centro de Custos")
    linhas[i] = linhas[i].replace("DemonstraÃ§Ã£o das MutaÃ§Ãµes do PL (DemonstraÃ§Ã£o das MutaÃ§Ãµes do PL (DMPL))", "Demonstração das Mutações do PL (DMPL)")
    linhas[i] = linhas[i].replace("DemonstraÃ§Ã£o das MutaÃ§Ãµes do PL (DMPL)", "Demonstração das Mutações do PL (DMPL)")
    linhas[i] = linhas[i].replace("AnÃ¡lise BP", "Análise BP")
    linhas[i] = linhas[i].replace("AnÃ¡lise DFC", "Análise DFC")
    linhas[i] = linhas[i].replace("AnÃ¡lise Patrimonial (DVP)", "Análise Patrimonial (DVP)")
    linhas[i] = linhas[i].replace("AnÃ¡lise OrÃ§amentÃ¡ria (BO)", "Análise Orçamentária (BO)")
    linhas[i] = linhas[i].replace("AnÃ¡lise Financeira (BF)", "Análise Financeira (BF)")

arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Linha 8740 corrigida e mojibakes dos nomes amigaveis corrigidos.")
