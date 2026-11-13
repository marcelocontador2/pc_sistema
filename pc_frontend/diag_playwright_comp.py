from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    erros = []
    page.on("console", lambda msg: erros.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)
    page.on("pageerror", lambda err: erros.append(f"[pageerror] {err}"))
    
    print("1. Abrindo a tela de Composição...")
    page.goto("http://localhost:9994/composicao_receitas_despesas", timeout=30000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    print("2. Verificando se o checkbox existe...")
    checkbox = page.query_selector('.check-hist') or page.query_selector('.check-historico')
    if checkbox:
        print("   -> Checkbox encontrado. Marcando...")
        checkbox.check()
    else:
        print("   -> ERRO: Checkbox NÃO encontrado na tela!")
    
    print("3. Clicando no botão Exibir...")
    try:
        page.click('button:has-text("Exibir")')
        page.wait_for_timeout(3000)
        print("   -> Botão clicado.")
    except Exception as e:
        print(f"   -> ERRO ao clicar: {e}")
    
    print("\n4. ERROS DO CONSOLE:")
    if erros:
        for e in erros:
            print(f"   {e}")
    else:
        print("   Nenhum erro capturado.")
    
    print("\n5. VERIFICANDO O CONTEÚDO DAS TABELAS:")
    tabelas = page.query_selector_all("table")
    for i, tab in enumerate(tabelas):
        texto = tab.inner_text().strip()
        if texto and "Clique em" not in texto and len(texto) > 50:
            print(f"   Tabela {i}: PREENCHIDA (primeiros 200 chars):")
            print(f"     {texto[:200]}")
        else:
            print(f"   Tabela {i}: VAZIA ou 'Clique em'")
    
    browser.close()
