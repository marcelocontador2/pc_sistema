import shutil

arquivos = ["custo_pessoal_pdf_resumo.html", "custo_pessoal_pdf_completo.html"]

for arquivo in arquivos:
    with open(arquivo, "r", encoding="utf-8") as f:
        s = f.read()
    
    shutil.copy(arquivo, arquivo + ".bak_font_fix")
    
    # Substitui a fonte Segoe UI por Arial
    if "Segoe UI" in s:
        s = s.replace("'Segoe UI', sans-serif", "Arial, Helvetica, sans-serif")
        s = s.replace('"Segoe UI", sans-serif', "Arial, Helvetica, sans-serif")
        print(f"OK: Fonte alterada para Arial em {arquivo}.")
    else:
        print(f"AVISO: 'Segoe UI' não encontrada em {arquivo}.")
        
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(s)
