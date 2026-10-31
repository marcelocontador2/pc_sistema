from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Adicionar meta tags anti-cache no head
if 'http-equiv="Cache-Control"' not in conteudo:
    trecho_head = "<head>"
    meta_tags = '''<head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">'''
    conteudo = conteudo.replace(trecho_head, meta_tags, 1)
    print("OK: Meta tags anti-cache adicionadas!")
else:
    print("AVISO: Meta tags anti-cache ja existem")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
