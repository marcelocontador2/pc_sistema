import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/configuracoes.html"
shutil.copy2(arq, f"{arq}.bak_preview_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Atualiza a funcao carregarConfiguracoes para usar o nome do arquivo
antigo = """        function carregarConfiguracoes() {
            fetch('/api/configuracoes/entidade').then(r => r.json()).then(data => {
                for (const [key, value] of Object.entries(data)) {
                    const el = document.getElementById(key);
                    if (el && key !== 'logo_path') el.value = value || '';
                }
                if (data.logo_path) {
                    const nomeArq = data.logo_path.split(/[\\\\/]/).pop();
                    document.getElementById('preview-logo').innerHTML = '<img src="/static_logos/' + nomeArq + '" style="max-height: 80px; max-width: 200px;">';
                }
            });
        }"""

novo = """        function carregarConfiguracoes() {
            fetch('/api/configuracoes/entidade').then(r => r.json()).then(data => {
                for (const [key, value] of Object.entries(data)) {
                    const el = document.getElementById(key);
                    if (el && key !== 'logo_path') el.value = value || '';
                }
                const preview = document.getElementById('preview-logo');
                if (data.logo_path) {
                    // O backend salva so o nome do arquivo (ex: logo_a1b2c3d4.png)
                    let nomeArq = data.logo_path;
                    if (nomeArq.includes('/') || nomeArq.includes('\\\\')) {
                        nomeArq = nomeArq.split(/[\\\\/]/).pop();
                    }
                    preview.innerHTML = '<img src="/static_logos/' + encodeURIComponent(nomeArq) + '" style="max-height: 80px; max-width: 200px;" onerror="this.style.display=\\'none\\'; this.parentElement.innerHTML=\\'<p style=\\'color:#888\\'>Logo nao encontrada. Envie novamente.</p>\\'">';
                } else {
                    preview.innerHTML = '<p style="color: #888;">Nenhuma logo cadastrada.</p>';
                }
            }).catch(e => console.error(e));
        }"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao carregarConfiguracoes ajustada para o nome correto da logo.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando regex...")
    import re
    padrao = re.compile(r'function carregarConfiguracoes\(\) \{.*?\n        \}', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Funcao carregarConfiguracoes ajustada via regex.")
    else:
        print("[ERRO] Nao encontrei a funcao carregarConfiguracoes.")
