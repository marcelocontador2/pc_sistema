c = open('main.py', encoding='utf-8-sig').read()

# Encontra a função api_relatorio_v2 e substitui a lógica de início dos dados
# Primeiro, vamos localizar o trecho "inicio_dados" dentro da função ler_csv
trecho_antigo = '''            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break
            
            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1'''

trecho_novo = '''            # Encontra o início dos dados reais (primeira linha que começa com "01 - AF")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                linha_limpa = linha.strip().strip('"')
                if linha_limpa.startswith("01 - AF") or linha_limpa.startswith("1 - AF"):
                    inicio_dados = i
                    break'''

# Aplica a substituição
if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Lógica de início dos dados corrigida!")
else:
    print("[AVISO] Trecho não encontrado. Tentando substituição mais flexível...")
    import re
    padrao = r'inicio_dados = 0\s*\n\s*for i, linha in enumerate\(linhas\):\s*\n\s*if "Centro de Custo x Conta" in linha:\s*\n\s*inicio_dados = i \+ 1\s*\n\s*break\s*\n\s*\n\s*if inicio_dados < len\(linhas\) and "COFEN/BR" in linhas\[inicio_dados\]:\s*\n\s*inicio_dados \+= 1'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, trecho_novo, c, flags=re.DOTALL)
        print("[OK] Lógica substituída via regex!")
    else:
        print("[ERRO] Não foi possível encontrar o trecho. Verifique manualmente.")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
