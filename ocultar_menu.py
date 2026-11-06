import glob, os, re, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    if not os.path.exists(arq):
        continue
        
    c = open(arq, encoding="utf-8", errors="ignore").read()
    
    # Encontra a tag <a> que tem o id="menu-demonstracoes" e tambem o <ul> do submenu
    # Vamos substituir o <a> pelo mesmo <a> com display: none
    padrao = re.compile(r'<a\s+([^>]*?id="menu-demonstracoes"[^>]*?)>([\s\S]*?)</a>', re.IGNORECASE)
    
    def substituir(match):
        atributos = match.group(1) or ""
        texto = match.group(2) or ""
        # Remove onclick, class e style antigos
        atributos_limpos = re.sub(r'onclick="[^"]*"\s*', '', atributos)
        atributos_limpos = re.sub(r'class="[^"]*"\s*', '', atributos_limpos)
        atributos_limpos = re.sub(r'style="[^"]*"\s*', '', atributos_limpos)
        
        # Adiciona display: none
        return f'<a id="menu-demonstracoes" {atributos_limpos} style="display: none;">{texto}</a>'
        
    c_novo = padrao.sub(substituir, c)
    
    # Esconde tambem o submenu (a <ul> logo abaixo) para nao deixar espaco em branco
    c_novo = re.sub(r'<ul\s+([^>]*?id="submenu-demonstracoes"[^>]*?)>', r'<ul \1 style="display: none;">', c_novo)
    
    if c_novo != c:
        bak = f"{arq}.bak_hide_{ts}"
        shutil.copy2(arq, bak)
        open(arq, "w", encoding="utf-8").write(c_novo)
        alterados += 1
        print(f"[OK] {arq} - menu ocultado com display:none")

print(f"\n[OK] {alterados} arquivos alterados.")
