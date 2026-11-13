arquivos = ["custo_pessoal_pdf_resumo.html", "custo_pessoal_pdf_completo.html"]

for arquivo in arquivos:
    print(f"\n=== TESTANDO {arquivo} ===")
    
    # 1. Tenta ler como UTF-8 estrito
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        print("  -> Lido como UTF-8 estrito: SUCESSO.")
        if "Resolução" in conteudo:
            print("  -> A palavra 'Resolução' ESTÁ no arquivo. (Encoding correto)")
        elif "Resoluo" in conteudo:
            print("  -> A palavra 'Resoluo' (sem acento) está no arquivo. O arquivo está corrompido no disco.")
        else:
            print("  -> Não achei 'Resolução' nem 'Resoluo' no arquivo.")
            
    except UnicodeDecodeError as e:
        print(f"  -> ERRO ao ler como UTF-8: {e}")
        print("  -> O arquivo definitivamente NÃO está em UTF-8!")
        
        # 2. Tenta ler como Windows-1252 (padrão ANSI do Windows)
        with open(arquivo, "r", encoding="cp1252") as f:
            conteudo_ansi = f.read()
        if "Resolução" in conteudo_ansi:
            print("  -> A palavra 'Resolução' ESTÁ no arquivo quando lido como ANSI (cp1252).")
            print("  -> VAMOS CORRIGIR: Convertendo de ANSI para UTF-8...")
            
            # Salva o backup e converte para UTF-8
            import shutil
            shutil.copy(arquivo, arquivo + ".bak_ansi")
            with open(arquivo, "w", encoding="utf-8") as f_out:
                f_out.write(conteudo_ansi)
            print("  -> ARQUIVO CONVERTIDO PARA UTF-8 COM SUCESSO!")
        else:
            print("  -> Nem lendo como ANSI achamos 'Resolução'. O texto está realmente corrompido no disco.")
