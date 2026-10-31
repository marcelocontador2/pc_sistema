from pathlib import Path

arquivo = Path("pc_frontend/configuracoes.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Adicionar o botao "Voltar" laranja no topo da tela
if "btn-voltar-config" not in conteudo:
    trecho_body = "<body>"
    btn_voltar = '''<body>
    <div style="padding: 15px 40px 0 40px;">
        <a href="/analise_custo_pessoal" style="display: inline-block; background: #fd7e14; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-family: 'Segoe UI', sans-serif;">← Voltar</a>
    </div>'''
    conteudo = conteudo.replace(trecho_body, btn_voltar, 1)
    arquivo.write_text(conteudo, encoding="utf-8")
    print("OK: Botao 'Voltar' laranja adicionado na tela de configuracoes!")
else:
    print("AVISO: Botao 'Voltar' ja existe")
