import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_historico")

# Encontra a função verificarEGerar
idx_inicio = html.find("async function verificarEGerar(")
if idx_inicio == -1:
    idx_inicio = html.find("function verificarEGerar(")

if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    # Nova função: carrega o último histórico salvo automaticamente
    nova_verificar = '''async function verificarEGerar() {
        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Carregando a matriz mais recente...</div>';

        try {
            // 1. Recarrega a lista lateral de históricos
            await carregarHistorico();

            // 2. Pega o primeiro histórico (o mais recente) e exibe
            const list = document.getElementById('lista-historico');
            if (list && list.children.length > 0) {
                list.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
                const primeiroCheckbox = list.querySelector('input[type="checkbox"]');
                
                if (primeiroCheckbox) {
                    primeiroCheckbox.checked = true;
                    // A função exibirSelecionado() busca o JSON no banco e renderiza os 23 itens
                    await exibirSelecionado(); 
                }
            } else {
                if (container) container.innerHTML = '<div style="padding: 20px; color: orange;">Nenhum histórico salvo. Gere uma matriz primeiro.</div>';
            }

        } catch (err) {
            console.error("Erro:", err);
            if (container) container.innerHTML = '<div style="color: red; padding: 20px;">Erro ao carregar histórico.</div>';
        }
    }'''

    html = html[:idx_inicio] + nova_verificar + html[i:]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'verificarEGerar' agora carrega o último histórico automaticamente!")
else:
    print("❌ Função 'verificarEGerar' não encontrada.")
