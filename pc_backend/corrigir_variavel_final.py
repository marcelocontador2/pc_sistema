import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Encontra a assinatura da função upload_arquivo
padrao_assinatura = r'(async def upload_arquivo\(.*?\):)'
match = re.search(padrao_assinatura, c, re.DOTALL)

if match:
    assinatura = match.group(1)
    # Verifica se dados_processados já está inicializado logo após a assinatura
    pos_assinatura = match.end()
    trecho_depois = c[pos_assinatura:pos_assinatura+500]
    
    if 'dados_processados = []' not in trecho_depois:
        # Insere a inicialização
        c = c[:pos_assinatura] + '\n    dados_processados = []\n    mensagem = "Arquivo enviado com sucesso."\n    centros = []' + c[pos_assinatura:]
        print("[OK] Variáveis inicializadas no início da função!")
    else:
        print("[AVISO] Variáveis já inicializadas.")
    
    # 2. Corrige o return para usar dados_processados corretamente
    c = c.replace(
        '"dados_processados": dados_processados',
        '"dados_processados": dados_processados if "dados_processados" in locals() else []'
    )
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] main.py corrigido!")
else:
    print("[ERRO] Função upload_arquivo não encontrada.")
