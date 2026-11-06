import re, os

for nome in ["analise_comparativo_receitas.html", "analise_comparativo_despesas.html"]:
    caminho = os.path.join("pc_frontend", nome)
    with open(caminho, "r", encoding="utf-8") as f:
        txt = f.read()
    
    print(f"\n{'='*60}")
    print(f"ARQUIVO: {nome}")
    print('='*60)
    
    # 1. Procura por qualquer função que tenha "historico" no nome
    funcs = re.findall(r'function\s+(\w*[hH]ist\w*)\s*\(', txt)
    if funcs:
        print(f"Funções encontradas: {funcs}")
        for func in funcs:
            idx = txt.find(f"function {func}")
            if idx != -1:
                print(f"\n--- {func} ---")
                print(txt[idx:idx+800])
    else:
        print("Nenhuma função com 'historico' no nome.")
    
    # 2. Procura por todos os checkboxes no HTML
    print("\n--- CHECKBOXES NO HTML ---")
    for m in re.finditer(r'<input[^>]*type="checkbox"[^>]*>', txt):
        print(m.group(0))
    
    # 3. Procura pela div do histórico
    print("\n--- DIV DO HISTÓRICO ---")
    for m in re.finditer(r'<div[^>]*id="[^"]*hist[^"]*"[^>]*>.*?</div>', txt, re.DOTALL | re.IGNORECASE):
        print(m.group(0)[:200])
    
    # 4. Mostra o trecho do fetch do histórico
    print("\n--- TRECHO DO FETCH DE HISTÓRICO ---")
    idx_fetch = txt.find("historico_comparativo")
    if idx_fetch != -1:
        print(txt[max(0, idx_fetch-200):idx_fetch+500])
