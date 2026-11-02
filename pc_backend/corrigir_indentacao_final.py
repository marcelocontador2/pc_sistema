c = open('main.py', encoding='utf-8-sig').read()

# 1. Corrige a indentação da linha 'mensagem = f"Centro de Custos importado...'
c = c.replace(
    '                        mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros) - Arquivo: {nome_arquivo}"',
    '                mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros) - Arquivo: {nome_arquivo}"'
)

# 2. Restaura a variável dados_processados antes do return (para o retorno não quebrar)
# Verifica se o return já tem dados_processados
if '"dados_processados": dados_processados' in c and 'dados_processados = centros' not in c:
    # Adiciona a atribuição logo antes do return
    c = c.replace(
        '        "dados_processados": dados_processados',
        '        "dados_processados": centros if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS" else []'
    )
    print("[OK] Retorno do dados_processados corrigido!")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Indentação corrigida!")
