from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Captura erros do console
    erros = []
    page.on("console", lambda msg: erros.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
    page.on("pageerror", lambda err: erros.append(f"PAGE ERROR: {err}"))
    
    page.goto("http://127.0.0.1:9994/analise_comparativo_despesas")
    page.wait_for_timeout(2000)
    
    # Verifica se as funções existem no contexto do navegador
    tem_verificar = page.evaluate("typeof verificar === 'function'")
    tem_exibir = page.evaluate("typeof exibirSelecionado === 'function'")
    tem_render = page.evaluate("typeof renderizarTabela === 'function'")
    tem_cards = page.evaluate("typeof atualizarCards === 'function'")
    
    print(f"verificar: {tem_verificar}")
    print(f"exibirSelecionado: {tem_exibir}")
    print(f"renderizarTabela: {tem_render}")
    print(f"atualizarCards: {tem_cards}")
    
    # Executa o verificar
    print("\nExecutando verificar()...")
    page.evaluate("verificar()")
    page.wait_for_timeout(3000)
    
    # Verifica o conteúdo da tabela
    tabela = page.evaluate("document.getElementById('tabela-container').innerHTML")
    print(f"\nTabela tem {len(tabela)} caracteres")
    if len(tabela) > 100:
        print("✅ Tabela renderizada! Primeiros 500 chars:")
        print(tabela[:500])
    else:
        print(f"❌ Tabela vazia ou com erro: {tabela[:500]}")
    
    # Mostra erros
    if erros:
        print(f"\n❌ {len(erros)} erros encontrados:")
        for e in erros:
            print(f"   {e}")
    else:
        print("\n✅ Nenhum erro no console do navegador.")
    
    browser.close()
