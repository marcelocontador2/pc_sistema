import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/configuracoes.html"
shutil.copy2(arq, f"{arq}.bak_alerta_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Substitui a funcao salvarConfiguracoes por uma versao que garante o alerta
antigo = """        function salvarConfiguracoes() {
            const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
            const dados = {};
            campos.forEach(c => { const el = document.getElementById(c); if (el) dados[c] = el.value; });
            fetch('/api/configuracoes/entidade', {
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(dados)
            }).then(r => r.json()).then(data => {
                if (data.ok) {
                    const msg = document.getElementById('msg-sucesso');
                    msg.style.display = 'block';
                    setTimeout(() => { msg.style.display = 'none'; }, 3000);
                } else { alert("Erro: " + (data.mensagem || "Falha")); }
            });
        }"""

novo = """        function salvarConfiguracoes() {
            const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
            const dados = {};
            campos.forEach(c => { const el = document.getElementById(c); if (el) dados[c] = el.value; });
            
            const btn = event.target;
            const textoOriginal = btn.innerText;
            btn.innerText = "Salvando...";
            btn.disabled = true;

            fetch('/api/configuracoes/entidade', {
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify(dados)
            })
            .then(r => {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            })
            .then(data => {
                if (data.ok) {
                    // Mostra o alerta verde
                    const msg = document.getElementById('msg-sucesso');
                    msg.style.display = 'block';
                    // Garante que a mensagem fique visivel por pelo menos 4 segundos
                    msg.scrollIntoView({behavior: 'smooth', block: 'center'});
                    setTimeout(() => { msg.style.display = 'none'; }, 4000);
                    // Fallback: mostra alert nativo tambem, para garantir visibilidade
                    alert("Configuracoes salvas com sucesso!");
                } else { 
                    alert("Erro: " + (data.mensagem || "Falha ao salvar.")); 
                }
            })
            .catch(e => {
                alert("Erro de conexao: " + e.message);
            })
            .finally(() => {
                btn.innerText = textoOriginal;
                btn.disabled = false;
            });
        }"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao salvarConfiguracoes ajustada com alerta garantido.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando regex...")
    import re
    padrao = re.compile(r'function salvarConfiguracoes\(\) \{.*?\n        \}', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Funcao ajustada via regex.")
    else:
        print("[ERRO] Nao foi possivel encontrar a funcao salvarConfiguracoes.")
