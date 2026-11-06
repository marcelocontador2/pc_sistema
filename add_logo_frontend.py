import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/configuracoes.html"
shutil.copy2(arq, f"{arq}.bak_logo_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Adiciona o bloco de upload da logo no HTML, logo apos o <h1>
antigo_html = """        <h1>Configuracoes - Cadastro da Entidade</h1>
        <div id="msg-sucesso" class="msg-sucesso">Configuracoes salvas com sucesso!</div>"""

novo_html = """        <h1>Configuracoes - Cadastro da Entidade</h1>
        <div id="msg-sucesso" class="msg-sucesso">Configuracoes salvas com sucesso!</div>

        <!-- UPLOAD DE LOGO -->
        <div style="margin-top: 20px; padding: 20px; background: #f8f9fa; border: 2px dashed #ccc; border-radius: 8px; text-align: center;">
            <h3 style="margin-top: 0; color: #003366;">Logo da Entidade</h3>
            <div id="preview-logo" style="margin-bottom: 15px;">
                <p style="color: #888;">Nenhuma logo cadastrada.</p>
            </div>
            <input type="file" id="input-logo" accept=".png,.jpg,.jpeg" style="display: none;" onchange="uploadLogo()">
            <button class="btn btn-voltar" onclick="document.getElementById('input-logo').click()" style="background: #0056b3;">
                Selecionar Logo (PNG / JPG)
            </button>
        </div>"""

if antigo_html in c:
    c = c.replace(antigo_html, novo_html, 1)
    print("[OK] Bloco de upload de logo adicionado no HTML.")

# 2. Adiciona a funcao uploadLogo e ajusta carregarConfiguracoes
antigo_js = """        function carregarConfiguracoes() {
            fetch('/api/configuracoes/entidade').then(r => r.json()).then(data => {
                for (const [key, value] of Object.entries(data)) {
                    const el = document.getElementById(key);
                    if (el) el.value = value || '';
                }
            });
        }"""

novo_js = """        function carregarConfiguracoes() {
            fetch('/api/configuracoes/entidade').then(r => r.json()).then(data => {
                for (const [key, value] of Object.entries(data)) {
                    const el = document.getElementById(key);
                    if (el && key !== 'logo_path') el.value = value || '';
                }
                // Preview da logo
                if (data.logo_path) {
                    const nomeArq = data.logo_path.split(/[\\\\/]/).pop();
                    document.getElementById('preview-logo').innerHTML = '<img src="/static_logos/' + nomeArq + '" style="max-height: 80px; max-width: 200px;">';
                }
            });
        }

        function uploadLogo() {
            const input = document.getElementById('input-logo');
            if (!input.files || input.files.length === 0) return;
            
            const formData = new FormData();
            formData.append('file', input.files[0]);
            
            fetch('/api/configuracoes/logo', {
                method: 'POST',
                body: formData
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    alert("Logo enviada com sucesso!");
                    carregarConfiguracoes();
                } else {
                    alert("Erro: " + (data.mensagem || "Falha no upload."));
                }
            })
            .catch(e => alert("Erro de conexao: " + e.message));
        }"""

if antigo_js in c:
    c = c.replace(antigo_js, novo_js, 1)
    print("[OK] Funcao uploadLogo e preview adicionadas.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend atualizado.")
