import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Atualiza a lista linksParaMover para incluir os 4 itens que faltam
    padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
    match = padrao.search(c)
    if match:
        lista_atual = match.group(2)
        # Verifica se os 4 itens ja estao na lista
        itens_faltando = ['Comparativo de Receitas', 'Comparativo de Despesas', 'Análise por Centro de Custos', 'Custo de Pessoal']
        for item in itens_faltando:
            if f"'{item}'" not in lista_atual:
                lista_atual = lista_atual.rstrip() + f",\n        '{item}'"
                print(f"[OK] {arq} - '{item}' adicionado à lista linksParaMover.")
        
        c = c[:match.start(2)] + lista_atual + c[match.end(2):]
        print(f"[OK] {arq} - Lista linksParaMover atualizada.")
    else:
        print(f"[AVISO] {arq} - Lista linksParaMover nao encontrada.")

    # 2. Garante que os 4 links estao no HTML estatico (na ordem correta)
    # Procura o ultimo link existente (Resultados Gerais) e insere os 4 depois
    idx_ultimo = c.find('Resultados Gerais')
    if idx_ultimo != -1:
        # Encontra o fechamento do </li> ou </a> do "Resultados Gerais"
        end_tag = c.find('</li>', idx_ultimo) + 5
        if end_tag == -1:
            end_tag = c.find('</a>', idx_ultimo) + 4
        if end_tag == -1:
            end_tag = idx_ultimo + 100

        # Verifica se os 4 links ja estao no HTML
        links_faltando = []
        for link, texto in [
            ('/comparativo_receitas', 'Comparativo de Receitas'),
            ('/comparativo_despesas', 'Comparativo de Despesas'),
            ('/centro_custos', 'Análise por Centro de Custos'),
            ('/custo_pessoal', 'Custo de Pessoal')
        ]:
            if f'href="{link}"' not in c:
                links_faltando.append((link, texto))

        if links_faltando:
            bloco_novo = ''
            for link, texto in links_faltando:
                bloco_novo += f'\n            <a href="{link}" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">{texto}</a>'
                print(f"[OK] {arq} - '{texto}' adicionado ao HTML estático.")
            
            c = c[:end_tag] + bloco_novo + c[end_tag:]
        else:
            print(f"[INFO] {arq} - Todos os 4 links já estão no HTML estático.")
    else:
        print(f"[AVISO] {arq} - 'Resultados Gerais' nao encontrado no HTML.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_add_4links_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
