c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

if "configuracoes_custo_pessoal" not in c:
    # Insere o botão de configurações antes do botão "Verificar Análise"
    c = c.replace(
        '<button class="btn" onclick="verificarAnalise()">Verificar Análise</button>',
        '<a href="/configuracoes_custo_pessoal" class="btn" style="background-color: #6c757d; text-decoration: none; display: inline-block; text-align: center; margin-right: 10px;">Configurações</a><button class="btn" onclick="verificarAnalise()">Verificar Análise</button>'
    )
    # Fallback se não encontrar a estrutura exata (antes do "Gerar PDF")
    if "configuracoes_custo_pessoal" not in c:
         c = c.replace(
            '<button class="btn" onclick="gerarPDF()">Gerar PDF</button>',
            '<a href="/configuracoes_custo_pessoal" class="btn" style="background-color: #6c757d; text-decoration: none; display: inline-block; text-align: center;">Configurações</a> <button class="btn" onclick="gerarPDF()">Gerar PDF</button>'
        )

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print('[OK] Botão de configurações adicionado na tela principal!')
