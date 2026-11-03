import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra a função upload_arquivo
inicio = c.find('async def upload_arquivo')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
else:
    # Encontra o fim da função
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio + 10)
        if pos != -1 and pos < fim:
            fim = pos
    
    bloco = c[inicio:fim]
    
    # Procura o trecho onde o nome_arquivo é definido
    # O padrão atual deve ser algo como: if tipo_relatorio.upper() == "CENTRO_CUSTOS": ... nome_arquivo = ...
    # Vamos adicionar o tratamento para COMPARATIVO_RECEITAS
    if 'COMPARATIVO_RECEITAS' not in bloco or 'nome_arquivo = f"COMPARATIVO_RECEITAS' not in bloco:
        # Encontra o local onde o nome_arquivo é definido (antes do open para salvar)
        # Vamos inserir a lógica antes do bloco de salvamento
        trecho_nome = 'nome_arquivo = file.filename'
        if trecho_nome in bloco:
            # Adiciona o tratamento para COMPARATIVO_RECEITAS logo após a definição inicial
            novo_trecho = '''nome_arquivo = file.filename
    if tipo_relatorio and tipo_relatorio.upper() == "COMPARATIVO_RECEITAS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"'''
            bloco = bloco.replace(trecho_nome, novo_trecho)
            c = c[:inicio] + bloco + c[fim:]
            print("[OK] Lógica de padronização para COMPARATIVO_RECEITAS adicionada!")
        else:
            print("[AVISO] Trecho 'nome_arquivo = file.filename' não encontrado. Tentando outra abordagem...")
            # Se não encontrar, tenta encontrar onde o arquivo é salvo e adicionar antes
            # Mas vamos tentar uma substituição mais ampla
            if 'caminho = os.path.join(UPLOAD_DIR, nome_arquivo)' in bloco:
                # Insere a lógica antes da linha que define o caminho
                bloco = bloco.replace(
                    'caminho = os.path.join(UPLOAD_DIR, nome_arquivo)',
                    '''if tipo_relatorio and tipo_relatorio.upper() == "COMPARATIVO_RECEITAS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)'''
                )
                c = c[:inicio] + bloco + c[fim:]
                print("[OK] Lógica adicionada antes do caminho!")
            else:
                print("[ERRO] Não foi possível encontrar o local para inserir a lógica.")
    else:
        print("[AVISO] A lógica para COMPARATIVO_RECEITAS já existe.")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
