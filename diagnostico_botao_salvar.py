import re

print("🔍 [1/2] INSPECIONANDO O HTML...")
caminho_html = "pc_frontend/relatorio_consolidado.html"
with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Verifica se o botão está lá
if 'id="btn-salvar-consolidado"' in html:
    print("✅ Botão HTML 'Confirmar e Salvar' ENCONTRADO.")
    # Mostra a linha exata para verificar o onclick
    for i, linha in enumerate(html.split("\n")):
        if 'btn-salvar-consolidado' in linha:
            print(f"   Linha {i+1}: {linha.strip()[:200]}")
            break
else:
    print("❌ Botão HTML 'Confirmar e Salvar' NÃO ENCONTRADO.")

# Verifica se a função JS existe
if "salvarRelatorioConsolidado" in html:
    print("✅ Função 'salvarRelatorioConsolidado' ENCONTRADA no HTML.")
    # Mostra a linha da definição
    for i, linha in enumerate(html.split("\n")):
        if "function salvarRelatorioConsolidado" in linha:
            print(f"   Linha {i+1}: {linha.strip()[:150]}")
            break
else:
    print("❌ Função 'salvarRelatorioConsolidado' NÃO ENCONTRADA no HTML.")

# Verifica se a rota é chamada corretamente na função
if "salvar_relatorio_consolidado" in html:
    print("✅ Rota '/salvar_relatorio_consolidado' está sendo chamada no fetch.")
else:
    print("❌ Rota '/salvar_relatorio_consolidado' NÃO está sendo chamada.")

print("\n" + "="*60)

print("🔍 [2/2] INSPECIONANDO O BACKEND (main.py)...")
caminho_main = "pc_backend/main.py"
with open(caminho_main, "r", encoding="utf-8") as f:
    main_content = f.read()

# Verifica se a rota de salvar existe
if '@app.post("/salvar_relatorio_consolidado/{periodo}")' in main_content:
    print("✅ Rota '@app.post(\"/salvar_relatorio_consolidado/{periodo}\")' ENCONTRADA no backend.")
    # Mostra a função (primeiras 20 linhas)
    idx = main_content.find('@app.post("/salvar_relatorio_consolidado/{periodo}")')
    if idx != -1:
        bloco = main_content[idx:idx+1500]
        print("   Primeiras linhas da função:")
        for linha in bloco.split("\n")[:15]:
            print(f"   {linha.strip()}")
else:
    print("❌ Rota '@app.post(\"/salvar_relatorio_consolidado/{periodo}\")' NÃO ENCONTRADA no backend.")
