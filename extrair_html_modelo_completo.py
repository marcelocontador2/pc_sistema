import fitz
import os
import shutil

caminho_pdf = "MODELO - relatorio_consolidado_29 - 3º trimestre 2026.pdf"

if not os.path.exists(caminho_pdf):
    print(f"❌ Arquivo não encontrado: {caminho_pdf}")
else:
    print(f"✅ Arquivo encontrado: {caminho_pdf}")
    print("   Tamanho: {:.2f} KB".format(os.path.getsize(caminho_pdf) / 1024))
    
    doc = fitz.open(caminho_pdf)
    print(f"   Páginas: {doc.page_count}")
    
    # Extrai o HTML de cada página e salva em arquivos separados
    for i in range(min(doc.page_count, 17)):  # Até 17 páginas
        pagina = doc[i]
        html = pagina.get_text("html")
        with open(f"modelo_pagina_{i+1}.html", "w", encoding="utf-8") as f:
            f.write(html)
    
    print(f"\n✅ HTML extraído para modelo_pagina_1.html até modelo_pagina_{min(doc.page_count, 17)}.html")
    
    # Mostra as primeiras 30 linhas da página 2 (Integridade)
    print("\n📄 Primeiras 30 linhas do HTML da página 2 (Integridade):")
    print("-" * 70)
    with open("modelo_pagina_2.html", "r", encoding="utf-8") as f:
        for i, linha in enumerate(f):
            if i >= 30:
                break
            print(linha.rstrip())
    print("-" * 70)
    
    doc.close()
