import os, re

print("=== 1. ARQUIVOS DE COMPARATIVO ===")
for nome in os.listdir("pc_frontend"):
    if "comparativo" in nome.lower() and nome.endswith(".html"):
        print(f" - {nome}")

print("\n=== 2. FUNÇÕES DE EXCLUSÃO NOS ARQUIVOS ENCONTRADOS ===")
for nome in os.listdir("pc_frontend"):
    if "comparativo" in nome.lower() and nome.endswith(".html"):
        caminho = os.path.join("pc_frontend", nome)
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        
        # Procura qualquer função que tenha "excluir" no nome
        funcs = re.findall(r'(?:async\s+)?function\s+(excluir\w*)\s*\(', txt)
        if funcs:
            print(f"\nArquivo: {nome}")
            print(f"  Funções: {funcs}")
            
            # Mostra o botão que chama a função
            for func in funcs:
                botoes = re.findall(rf'<button[^>]*onclick="[^"]*{func}[^"]*"[^>]*>.*?</button>', txt, re.DOTALL)
                for btn in botoes:
                    print(f"  Botão: {btn[:150].replace(chr(10),' ')}...")
        else:
            # Se não tem função, talvez o botão esteja inline ou em outro arquivo JS
            print(f"\nArquivo: {nome} (nenhuma função 'excluir' encontrada)")
            # Procura botão de excluir
            btn = re.search(r'<button[^>]*>\s*Excluir.*?</button>', txt, re.DOTALL | re.IGNORECASE)
            if btn:
                print(f"  Botão encontrado: {btn.group(0)[:200].replace(chr(10),' ')}...")
