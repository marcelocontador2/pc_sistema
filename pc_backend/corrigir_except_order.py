c = open('main.py', encoding='utf-8-sig').read()

# Encontra o trecho com os except fora de ordem
trecho_antigo = '''            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
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

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Bloco except corrigido!")
else:
    print("[AVISO] Trecho exato não encontrado. Tentando substituição via regex...")
    import re
    # Remove except duplicado
    padrao = r'(except:\s*\n\s*with open\(arquivo, "r", encoding="utf-8", errors="ignore"\) as f:\s*\n\s*linhas = f\.readlines\(\))\s*\n\s*except:\s*\n\s*with open\(arquivo, "r", encoding="utf-8", errors="ignore"\) as f:\s*\n\s*linhas = f\.readlines\(\)'
    c = re.sub(padrao, r'\1', c, flags=re.DOTALL)
    print("[OK] Except duplicado removido via regex!")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
