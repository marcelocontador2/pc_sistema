import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bp_sem_rs")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise BP
idx_bp = conteudo.find('elif nome_interno == "Análise BP":')
if idx_bp != -1:
    idx_fim_bp = conteudo.find('elif nome_interno ==', idx_bp + 10)
    if idx_fim_bp == -1:
        idx_fim_bp = conteudo.find('except Exception', idx_bp)
    
    bloco_bp = conteudo[idx_bp:idx_fim_bp]
    
    # Substitui a função 'fmt' por uma versão sem R$ apenas neste bloco
    # Primeiro, adiciona a função local 'fmt_sem_rs'
    nova_abertura = '''elif nome_interno == "Análise BP":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    dados_bp = mod_dados.get("dados", {})'''
    
    # Substitui a linha de abertura do bloco
    bloco_bp = bloco_bp.replace('elif nome_interno == "Análise BP":\n                    dados_bp = mod_dados.get("dados", {})', nova_abertura)
    
    # Substitui todas as chamadas 'fmt(' por 'fmt_sem_rs(' neste bloco
    bloco_bp = bloco_bp.replace('{fmt(', '{fmt_sem_rs(')
    bloco_bp = bloco_bp.replace('fmt(', 'fmt_sem_rs(')
    
    # Restaura a chamada da função original para o gráfico (que usa fmt para os labels, mas não precisa)
    # (O gráfico usa json.dumps(atual_vals), que já é numérico, então não afeta)
    
    conteudo = conteudo[:idx_bp] + bloco_bp + conteudo[idx_fim_bp:]
    print("✅ Item 2 (BP) ajustado para exibir valores sem 'R$'.")
else:
    print("❌ Bloco da Análise BP não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
