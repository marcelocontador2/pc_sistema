from pathlib import Path

arquivo = Path("pc_frontend/analise_dvp.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Injeta um aviso visível logo após o <body>
aviso = """
<div style="background: red; color: white; font-size: 30px; text-align: center; padding: 20px; font-weight: bold;">
    🚨 TESTE DE FUMAÇA: SE VOCÊ ESTÁ VENDO ISSO, O HTML FOI ATUALIZADO! 🚨
</div>
"""

if "TESTE DE FUMAÇA" not in conteudo:
    # Tenta achar a tag body
    if "<body>" in conteudo:
        conteudo = conteudo.replace("<body>", "<body>" + aviso, 1)
        arquivo.write_text(conteudo, encoding="utf-8")
        print("OK: Aviso injetado no HTML.")
    else:
        print("ERRO: Tag <body> não encontrada no HTML.")
else:
    print("AVISO: O teste já foi injetado antes.")
