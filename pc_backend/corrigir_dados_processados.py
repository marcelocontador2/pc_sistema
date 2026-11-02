c = open('main.py', encoding='utf-8-sig').read()

# 1. Encontra o início da função upload_arquivo
inicio_funcao = c.find('async def upload_arquivo')
if inicio_funcao == -1:
    print("[ERRO] Função upload_arquivo não encontrada.")
else:
    # Encontra o final da assinatura (o primeiro "):")
    fim_assinatura = c.find('):', inicio_funcao) + 2
    if fim_assinatura != -1:
        # Adiciona a inicialização da variável logo após a assinatura
        trecho_inicializacao = '\n    dados_processados = []\n    mensagem = "Arquivo enviado com sucesso."\n    centros = []'
        
        # Verifica se já está inicializado (para não duplicar)
        trecho_antes = c[inicio_funcao:fim_assinatura]
        if 'dados_processados = []' not in trecho_antes:
            c = c[:fim_assinatura] + trecho_inicializacao + c[fim_assinatura:]
            print("[OK] Variável 'dados_processados' inicializada no início da função!")
        else:
            print("[AVISO] A variável já está inicializada.")

# 2. Remove inicializações duplicadas dentro do bloco if (opcional, para limpar)
c = c.replace('        dados_processados = centros\n', '')
c = c.replace('    dados_processados = centros\n', '')

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py corrigido!")
