c = open('main.py', encoding='utf-8-sig').read()

# Remove o except duplicado
c = c.replace(
    '''              except:
                  with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                      linhas = f.readlines()
              except:
                  with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                      linhas = f.readlines()''',
    '''              except:
                  with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                      linhas = f.readlines()'''
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Except duplicado removido!")
