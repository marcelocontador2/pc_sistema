import re

def auditar(arquivo):
    print(f"\n{'='*60}")
    print(f"AUDITANDO: {arquivo}")
    print(f"{'='*60}")
    with open(arquivo, "r", encoding="utf-8") as f:
        s = f.read()
    
    # 1. Achar o botao
    print("\n[1] BOTOES ENCONTRADOS:")
    botoes = re.findall(r'<button[^>]*>([^<]*)</button>', s)
    for b in botoes:
        if 'Exibir' in b or 'exibir' in b:
            # Pega a tag inteira
            match = re.search(r'<button[^>]*>' + re.escape(b) + r'</button>', s)
            if match:
                print(f"  {match.group(0)}")
                
    # 2. Achar a funcao exibirSelecionado
    print("\n[2] FUNCAO exibirSelecionado:")
    match = re.search(r'(async\s+)?function\s+exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
    if match:
        print(match.group(0)[:1000])
    else:
        print("  NAO ENCONTRADA!")
        
    # 3. Achar o event listener ou onclick
    print("\n[3] EVENT LISTENER OU ONCLICK:")
    for linha in s.split('\n'):
        if 'exibirSelecionado' in linha and ('addEventListener' in linha or 'onclick' in linha):
            print(f"  {linha.strip()}")

# Audita a Conferencia (que FUNCIONA)
auditar("conferencia.html")
# Audita o DMPL (que ESTA QUEBRADO)
auditar("analise_dmpl.html")
