c = open('../pc_frontend/configuracoes_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Troca a cor de fundo do botão voltar para laranja
c = c.replace(
    ".btn-voltar { background: #6c757d; color: white; }",
    ".btn-voltar { background: #ff8c00; color: white; }"
)

# 2. Troca a cor do hover (quando passa o mouse)
c = c.replace(
    ".btn-voltar:hover { background: #5c636a; }",
    ".btn-voltar:hover { background: #e67e00; }"
)

open('../pc_frontend/configuracoes_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Voltar para Análise' agora está laranja!")
