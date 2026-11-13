import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_capa_completa")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o trecho da capa (o primeiro html_parts.append com "legislacao")
idx_capa = conteudo.find('html_parts.append("<div class=\'legislacao\'>')

if idx_capa != -1:
    # Encontra o fim da linha (próximo \n)
    fim_linha = conteudo.find('\n', idx_capa)
    
    # Substitui pela capa completa com legislação e demonstrações
    nova_capa = '''html_parts.append("<div class='legislacao'>")
        html_parts.append("<strong>LEGISLAÇÃO E NORMAS APLICADAS:</strong><br>")
        html_parts.append("Lei nº 4.320/1964 (Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços.) • ")
        html_parts.append("Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil) • ")
        html_parts.append("Normas Brasileiras de Contabilidade – Setor Público (NBC TSP) • ")
        html_parts.append("Resolução COFEN nº 764/2024 (Prestação de Contas) • ")
        html_parts.append("Resolução Cofen nº 799/2025 (Gestão de riscos e controles internos) • ")
        html_parts.append("Resolução Cofen nº 814/2026 (Limites de despesa com pessoal) • ")
        html_parts.append("Manual de Contabilidade Aplicada ao Setor Público (MCASP)")
        html_parts.append("</div>")
        html_parts.append("<div class='legislacao' style='margin-top: 20px;'>")
        html_parts.append("<strong>DEMONSTRAÇÕES ANALISADAS:</strong><br>")
        html_parts.append("Balancete de Verificação • Balanço Financeiro (BF) • Balanço Orçamentário (BO) • Balanço Patrimonial (BP) • Demonstração do Fluxo de Caixa (DFC) • Demonstração das Mutações do PL (DMPL) • Demonstração das Variações Patrimoniais (DVP)")
        html_parts.append("</div>")'''
    
    conteudo = conteudo[:idx_capa] + nova_capa + conteudo[fim_linha:]

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ Capa atualizada com legislação e demonstrações completas.")
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
