import re
import os

arquivos = ["analise_bp.html", "analise_dmpl.html", "analise_patrimonial.html", "composicao_receitas_despesas.html"]

for arq in arquivos:
    if not os.path.exists(arq):
        print(f"Arquivo {arq} nao encontrado.")
        continue
    
    with open(arq, "r", encoding="utf-8") as f:
        s = f.read()
    
    print(f"\n{'='*70}")
    print(f"ARQUIVO: {arq}")
    print(f"{'='*70}")
    
    # Procura a funcao exibirSelecionado
    padrao = re.compile(r'(async\s+)?function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
    match = padrao.search(s)
    if match:
        print("=== FUNCAO exibirSelecionado ===")
        print(match.group(0)[:1500])
    else:
        print("Funcao exibirSelecionado NAO encontrada.")
    
    # Procura o botao Exibir
    print("\n=== BOTAO EXIBIR ===")
    for m in re.finditer(r'<button[^>]*>([^<]*Exibir[^<]*)</button>', s, re.IGNORECASE):
        print(m.group(0)[:200])
    
    # Procura os IDs das tabelas
    print("\n=== IDs DAS TABELAS ===")
    for m in re.finditer(r'<table[^>]*id="([^"]+)"', s):
        print(f"  - {m.group(1)}")
    
    # Procura as rotas fetch
    print("\n=== ROTAS FETCH ===")
    for m in re.finditer(r'fetch\(\s*[`\'"]([^`\'"]+)', s):
        print(f"  - {m.group(1)}")
