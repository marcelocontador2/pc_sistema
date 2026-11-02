import os
import re

for i in range(8):
    arquivo = f'script_{i}.js'
    if not os.path.exists(arquivo):
        continue
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Remove strings para não contar chaves dentro delas
    conteudo_limpo = re.sub(r'`.*?`', '', conteudo, flags=re.DOTALL)
    conteudo_limpo = re.sub(r'"[^"]*"', '', conteudo_limpo)
    conteudo_limpo = re.sub(r"'[^']*'", '', conteudo_limpo)
    
    abre = conteudo_limpo.count('{')
    fecha = conteudo_limpo.count('}')
    
    if abre != fecha:
        print(f"[ERRO] script_{i}.js: {abre} abertas, {fecha} fechadas (diferença: {abre - fecha})")
        # Mostra as últimas 100 linhas do arquivo para ajudar a localizar
        print(f"Últimas linhas do script_{i}.js:")
        linhas = conteudo.split('\n')
        for j in range(max(0, len(linhas)-10), len(linhas)):
            print(f"  {j+1}: {linhas[j][:100]}")
    else:
        print(f"[OK] script_{i}.js: chaves balanceadas.")
