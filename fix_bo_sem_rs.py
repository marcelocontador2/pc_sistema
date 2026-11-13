import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bo_sem_rs")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise Orçamentária (BO)
idx_bo = conteudo.find('elif nome_interno == "Análise Orçamentária (BO)":')
if idx_bo != -1:
    idx_fim_bo = conteudo.find('elif nome_interno ==', idx_bo + 10)
    if idx_fim_bo == -1:
        idx_fim_bo = conteudo.find('except Exception', idx_bo)
    
    bloco_bo = conteudo[idx_bo:idx_fim_bo]
    
    # Adiciona a função local 'fmt_sem_rs' no início do bloco BO
    nova_abertura = '''elif nome_interno == "Análise Orçamentária (BO)":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    atual = mod_dados.get("atual", {})'''
    
    bloco_bo = bloco_bo.replace('elif nome_interno == "Análise Orçamentária (BO)":\n                    atual = mod_dados.get("atual", {})', nova_abertura)
    
    # Substitui as chamadas 'fmt(' por 'fmt_sem_rs(' dentro deste bloco
    bloco_bo = bloco_bo.replace('{fmt(', '{fmt_sem_rs(')
    
    conteudo = conteudo[:idx_bo] + bloco_bo + conteudo[idx_fim_bo:]
    print("✅ Item 3 (BO) ajustado para exibir valores sem 'R$'.")
else:
    print("❌ Bloco da Análise Orçamentária não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
