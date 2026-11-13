import os
import shutil

arquivos = ["custo_pessoal_pdf_resumo.html", "custo_pessoal_pdf_completo.html"]

for arquivo in arquivos:
    if not os.path.exists(arquivo):
        print(f"AVISO: {arquivo} não encontrado.")
        continue
    
    # Lê os primeiros bytes para ver se tem BOM (Byte Order Mark) ou encoding estranho
    with open(arquivo, "rb") as f:
        bytes_iniciais = f.read(10)
    
    print(f"\n--- Arquivo: {arquivo} ---")
    print(f"Bytes iniciais (HEX): {bytes_iniciais.hex()}")
    
    # Tenta ler como UTF-8 e como Latin-1 para ver se tem erro
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            _ = f.read()
        print("  -> O arquivo está codificado em UTF-8 no disco. OK!")
    except UnicodeDecodeError:
        print("  -> ERRO: O arquivo NÃO está em UTF-8 no disco! Pode estar em ANSI/Latin-1.")
    
    # Vamos forçar a meta tag com http-equiv e salvar novamente forçando UTF-8
    with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
        s = f.read()
    
    if 'http-equiv="Content-Type"' not in s:
        if "<head>" in s:
            s = s.replace("<head>", '<head>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">', 1)
        else:
            s = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n' + s
        
        # Salva forçando UTF-8 sem BOM
        with open(arquivo, "w", encoding="utf-8", newline='\n') as f:
            f.write(s)
        print("  -> Meta tag 'http-equiv' adicionada e arquivo salvo forçando UTF-8.")
    else:
        print("  -> Arquivo já possui a meta tag 'http-equiv'.")

print("\nPROCESSO CONCLUIDO! Teste o PDF novamente.")
