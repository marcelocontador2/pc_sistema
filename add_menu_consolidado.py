import glob, os, shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    if not os.path.exists(arq):
        continue
    
    shutil.copy2(arq, f"{arq}.bak_menu_consolidado_{ts}")
    c = open(arq, encoding="utf-8", errors="ignore").read()
    
    # 1. Remove link antigo do consolidado (se existir) para nao duplicar
    c = re.sub(r'\s*<li><a href="/relatorio_consolidado"[^>]*>.*?</a></li>', '', c)
    
    # 2. Procura o link de Configuracoes para inserir logo depois
    idx = c.find('href="/configuracoes"')
    if idx == -1:
        print(f"[AVISO] Nao encontrei o link de configuracoes em {arq}.")
        continue
        
    # Encontra o fechamento do </li> do link de configuracoes
    end_li = c.find('</li>', idx)
    if end_li != -1:
        novo_li = '\n    <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatorio Consolidado</a></li>'
        c = c[:end_li+5] + novo_li + c[end_li+5:]
        
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - link 'Relatorio Consolidado' adicionado abaixo de Configuracoes.")
    else:
        print(f"[AVISO] Nao encontrei o fechamento </li> em {arq}.")

print(f"\n[OK] {alterados} arquivos alterados.")
