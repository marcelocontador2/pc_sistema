import re

for arquivo in ["../pc_frontend/custo_pessoal_pdf_resumo.html", "../pc_frontend/custo_pessoal_pdf_completo.html"]:
    try:
        c = open(arquivo, encoding="utf-8-sig").read()
        
        # Substitui qualquer <td> que contenha 50,00% pelo padrão exato
        c = re.sub(r'<td[^>]*>\s*50,00%\s*</td>', '<td class="right">50,00%</td>', c)
        
        # Garante que o texto do limite também esteja no padrão
        c = re.sub(r'Limite Resolução Cofen 814/2026\s*\(50% da RCL\)', 'Limite Resolução Cofen 814/2026 (50% da RCL)', c)
        
        open(arquivo, "w", encoding="utf-8").write(c)
        print(f"[OK] HTML ajustado: {arquivo}")
    except FileNotFoundError:
        print(f"[AVISO] Arquivo não encontrado: {arquivo}")
