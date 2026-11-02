import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Substitui a leitura do CSV na função ler_csv_mensal
trecho_antigo = '''            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()'''

trecho_novo = '''            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()'''

c = c.replace(trecho_antigo, trecho_novo)

# 2. Substitui a leitura na função api_centro_custos
trecho_antigo2 = '''            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()'''

c = c.replace(trecho_antigo2, trecho_novo)

# 3. Substitui a leitura na função api_centro_custos (versão antiga, se existir)
trecho_antigo3 = '''        try:
            with open(arquivo, "r", encoding="utf-8-sig") as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin-1") as f:
                linhas = f.readlines()'''

trecho_novo3 = '''        try:
            with open(arquivo, "r", encoding="utf-8-sig") as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin-1") as f:
                linhas = f.readlines()
        except:
            with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                linhas = f.readlines()'''

c = c.replace(trecho_antigo3, trecho_novo3)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Leitura de CSV ajustada para lidar com ANSI e UTF-8!")
