import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_total_dispendios")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a linha que faz a busca do total de dispêndios
trecho_antigo = '''                        total_disp_atual, total_disp_ant = buscar_valor_dispendio(linhas, "Total:")'''
trecho_novo = '''                        # Busca direta na linha "Total:" pelas colunas 4 e 5
                        total_disp_atual = 0.0
                        total_disp_ant = 0.0
                        for linha in linhas:
                            if linha and len(linha) >= 6 and "Total:" in str(linha[0]):
                                total_disp_atual = limpar_valor(linha[4])
                                total_disp_ant = limpar_valor(linha[5])
                                break'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("✅ Busca do Total Geral de Dispêndios corrigida (colunas 4 e 5).")
else:
    print("⚠️ Trecho não encontrado. Tentando abordagem alternativa...")
    # Busca o bloco todo e substitui
    import re
    padrao = r'total_disp_atual,\s*total_disp_ant\s*=\s*buscar_valor_dispendio\(linhas,\s*"Total:"\)'
    if re.search(padrao, conteudo):
        conteudo = re.sub(
            padrao,
            '''total_disp_atual = 0.0
                        total_disp_ant = 0.0
                        for linha in linhas:
                            if linha and len(linha) >= 6 and "Total:" in str(linha[0]):
                                total_disp_atual = limpar_valor(linha[4])
                                total_disp_ant = limpar_valor(linha[5])
                                break''',
            conteudo
        )
        print("✅ Busca do Total Geral de Dispêndios corrigida via regex.")
    else:
        print("❌ Não foi possível localizar a linha do total de dispêndios.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
