import urllib.request
import re

print("=" * 60)
print("TESTE: O que o navegador recebe ao abrir a tela?")
print("=" * 60)

url = "http://127.0.0.1:9994/analise_comparativo_despesas"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        html = r.read().decode("utf-8")
    
    print(f"Status: 200 | Tamanho: {len(html)} caracteres")
    
    # Verifica se as funções estão no HTML servido
    funcoes = ['function verificar(', 'function exibirSelecionado(', 'function renderizarTabela(', 'function atualizarCards(']
    for f in funcoes:
        if f in html:
            print(f"✅ {f} encontrada")
        else:
            print(f"❌ {f} NÃO encontrada")
    
    # Verifica o botão
    if 'onclick="verificar()"' in html:
        print("✅ Botão Verificar com onclick=verificar()")
    else:
        print("❌ Botão Verificar SEM onclick=verificar()")
        # Mostra o trecho do botão
        idx = html.find('Verificar')
        if idx != -1:
            print(f"   Trecho: {html[max(0,idx-150):idx+50]}")
    
    # Mostra os primeiros 2000 caracteres do script
    idx = html.find('<script>')
    if idx != -1:
        print("\n--- Primeiros 2000 caracteres do <script> ---")
        print(html[idx:idx+2000])
    else:
        print("❌ Bloco <script> NÃO encontrado no HTML servido")
        
except Exception as e:
    print(f"❌ Erro ao acessar a URL: {e}")
