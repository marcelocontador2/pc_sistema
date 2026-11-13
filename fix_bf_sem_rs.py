import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bf_sem_rs")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a linha que formata os valores no item 4 (BF) e remove o R$
# A função 'fmt' é usada em várias partes, então vamos criar uma 'fmt_sem_rs' local para o BF
idx_bf = conteudo.find('elif nome_interno == "Análise Financeira (BF)":')
if idx_bf != -1:
    # Adiciona a função local 'fmt_sem_rs' no início do bloco BF
    nova_linha = '''elif nome_interno == "Análise Financeira (BF)":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    import csv
                    import os'''
    
    # Substitui a linha de abertura do bloco BF
    conteudo = conteudo.replace('elif nome_interno == "Análise Financeira (BF)":\n                    import csv\n                    import os', nova_linha)
    
    # Agora, dentro do bloco BF, substitui todas as chamadas 'fmt(' por 'fmt_sem_rs('
    # Encontra o fim do bloco BF para não afetar os outros itens
    idx_fim_bf = conteudo.find('elif nome_interno ==', idx_bf + 10)
    if idx_fim_bf == -1:
        idx_fim_bf = conteudo.find('except Exception', idx_bf)
    
    bloco_bf = conteudo[idx_bf:idx_fim_bf]
    bloco_bf = bloco_bf.replace('{fmt(', '{fmt_sem_rs(')
    bloco_bf = bloco_bf.replace('fmt(', 'fmt_sem_rs(')
    
    conteudo = conteudo[:idx_bf] + bloco_bf + conteudo[idx_fim_bf:]
    print("✅ Item 4 (BF) ajustado para exibir valores sem 'R$'.")
else:
    print("❌ Bloco da Análise Financeira não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
