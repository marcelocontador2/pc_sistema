import re

c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# Se o botão de configurações ainda não existe, injeta ele de forma agressiva
if "configuracoes_custo_pessoal" not in c:
    # Procura o botão "Gerar PDF" (que sabemos que existe pela imagem) e coloca o de config do lado
    c = re.sub(
        r'(<button[^>]*>Gerar PDF</button>)',
        r'<a href="/configuracoes_custo_pessoal" class="btn" style="background-color: #6c757d; text-decoration: none; display: inline-block; padding: 10px 20px; border-radius: 5px; color: white; margin-right: 10px; font-weight: bold;">⚙️ Configurações</a>\1',
        c
    )
    print("[OK] Botão 'Configurações' injetado ao lado do 'Gerar PDF'!")
else:
    print("[OK] O botão 'Configurações' já existe no HTML.")

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
