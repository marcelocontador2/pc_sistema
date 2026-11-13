import os

caminho = "pc_backend/matriz_integridade.py"

if not os.path.exists(caminho):
    print(f"❌ Arquivo {caminho} NÃO existe!")
else:
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    print("=" * 70)
    print("AUDITORIA DO ARQUIVO matriz_integridade.py")
    print("=" * 70)
    print(f"Tamanho: {len(conteudo)} caracteres")
    
    # Lista todas as funções definidas
    import re
    funcoes = re.findall(r'^def\s+(\w+)\s*\(', conteudo, re.MULTILINE)
    print(f"\n📋 Funções encontradas ({len(funcoes)}):")
    for f in funcoes:
        print(f"   - {f}")
    
    # Verifica se 'gerar_matriz' existe
    if 'gerar_matriz' in conteudo:
        print("\n✅ 'gerar_matriz' aparece no arquivo.")
        idx = conteudo.find('gerar_matriz')
        print(f"   Contexto: {conteudo[max(0,idx-100):idx+200]}")
    else:
        print("\n❌ 'gerar_matriz' NÃO aparece no arquivo!")
    
    # Mostra as primeiras 30 linhas
    print("\n📄 Primeiras 30 linhas do arquivo:")
    print("-" * 70)
    for i, linha in enumerate(conteudo.split("\n")[:30]):
        print(f"   {i+1:3d}: {linha}")
    print("-" * 70)
