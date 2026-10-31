import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Substitui a condição corrompida por uma versão robusta
trecho_antigo = 'if "OUTRAS DESPESAS VARIÃƒÂVEIS" in nome and "PESSOAL" in nome:'
trecho_novo = 'if "OUTRAS DESPESAS VARI" in nome.upper() and ("PESSOAL" in nome.upper() or "RGPS" in nome.upper()):'

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Condição de 'Outras Despesas' corrigida!")
else:
    # Fallback caso os caracteres estejam ligeiramente diferentes
    c = re.sub(r'if "OUTRAS DESPESAS VARI.*?VEIS" in nome and "PESSOAL" in nome:', 
               'if "OUTRAS DESPESAS VARI" in nome.upper() and ("PESSOAL" in nome.upper() or "RGPS" in nome.upper()):', 
               c)
    print("[OK] Condição de 'Outras Despesas' corrigida via regex!")

open('main.py', 'w', encoding='utf-8').write(c)
