import pymupdf
import os

caminho_pdf = "pc_storage/uploads_raw/MODELO - relatorio_consolidado_29 - 3º trimestre 2026.pdf"

if not os.path.exists(caminho_pdf):
    print(f"❌ Arquivo não encontrado: {caminho_pdf}")
else:
    print(f"✅ Arquivo encontrado: {caminho_pdf}")
    print("   Tamanho: {:.2f} KB".format(os.path.getsize(caminho_pdf) / 1024))
    
    doc = pymupdf.open(caminho_pdf)
    print(f"   Páginas: {doc.page_count}")
    
    # Extrai o HTML de cada página e salva em arquivos separados
    for i in range(min(doc.page_count, 17)):
        pagina = doc[i]
        html = pagina.get_text("html")
        with open(f"modelo_pagina_{i+1}.html", "w", encoding="utf-8") as f:
            f.write(html)
    
    print(f"\n✅ HTML extraído para modelo_pagina_1.html até modelo_pagina_{min(doc.page_count, 17)}.html")
    
    # Mostra a estrutura da página 2 (Integridade)
    print("\n" + "="*70)
    print("📄 ESTRUTURA DA PÁGINA 2 (INTEGRIDADE):")
    print("="*70)
    with open("modelo_pagina_2.html", "r", encoding="utf-8") as f:
        conteudo = f.read()
        print(conteudo[:3000])
    
    doc.close()
