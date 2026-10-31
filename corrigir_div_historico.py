from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Verificar se a div "historico" existe
if 'id="historico"' not in conteudo:
    print("A div 'historico' NAO existe. Adicionando...")
    # Procurar a div que contem "Historico Salvo"
    # (geralmente tem uma div com titulo "Histórico Salvo" e uma lista vazia)
    
    # Vamos adicionar a div logo apos o titulo "Histórico Salvo"
    # (procurar o texto "Histórico Salvo" ou "Historico Salvo")
    padrao = r'(<h[23][^>]*>Hist[óo]rico Salvo</h[23]>)'
    match = re.search(padrao, conteudo, re.IGNORECASE)
    
    if match:
        titulo = match.group(1)
        nova_div = titulo + '\n        <div id="historico"><p style="color:#666; padding:10px;">Carregando...</p></div>'
        conteudo = conteudo.replace(titulo, nova_div, 1)
        print("OK: Div 'historico' adicionada!")
    else:
        print("AVISO: nao achei o titulo 'Historico Salvo'")
else:
    print("OK: Div 'historico' ja existe")

# 2. Verificar se o carregarHistorico() esta sendo chamado
if "carregarHistorico()" in conteudo:
    print("OK: carregarHistorico() esta sendo chamado no JS")
else:
    print("AVISO: carregarHistorico() NAO esta sendo chamado")

# 3. Adicionar um botao de recarregar historico (opcional, para debug)
if "recarregarHistoricoBtn" not in conteudo:
    # Adicionar um botao ao lado do titulo
    padrao_titulo = r'(<h[23][^>]*>Hist[óo]rico Salvo</h[23]>)'
    match_titulo = re.search(padrao_titulo, conteudo, re.IGNORECASE)
    if match_titulo:
        titulo = match_titulo.group(1)
        botao = titulo + ' <button onclick="carregarHistorico()" style="font-size:12px; padding:5px 10px; cursor:pointer;">Recarregar</button>'
        conteudo = conteudo.replace(titulo, botao, 1)
        print("OK: Botao 'Recarregar' adicionado ao historico!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
