import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_verificar_original")

# Nova função que gera o histórico e exibe o último salvo
nova_verificar = '''
async function verificarEGerar() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    const trimestre = document.getElementById('trimestre').value;
    const periodo = `${ano}-${tipo}-${trimestre}`;

    const container = document.getElementById('integridade-cards');
    if (container) container.innerHTML = '<div class="loading">Gerando matriz...</div>';

    try {
        // 1. Salva a matriz (isso gera o histórico no formato original)
        const resSalvar = await fetch(`/api/integridade_matriz/${periodo}/salvar`, { method: 'POST' });
        const dataSalvar = await resSalvar.json();
        
        if (dataSalvar.erro) {
            alert("Erro ao gerar matriz: " + (dataSalvar.mensagem || "Erro desconhecido"));
            if (container) container.innerHTML = '';
            return;
        }

        // 2. Recarrega a lista de históricos
        await carregarHistorico();

        // 3. Pega o primeiro histórico da lista (o mais recente) e exibe
        const list = document.getElementById('lista-historico');
        if (list && list.children.length > 0) {
            // Desmarca todos
            list.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            
            // Marca o primeiro (mais recente)
            const primeiroCheckbox = list.querySelector('input[type="checkbox"]');
            if (primeiroCheckbox) {
                primeiroCheckbox.checked = true;
                // Exibe o histórico, que já renderiza o design original
                await exibirSelecionado();
            }
        } else {
            if (container) container.innerHTML = '<div class="loading">Nenhum histórico gerado.</div>';
        }
    } catch (err) {
        console.error(err);
        if (container) container.innerHTML = '<div class="loading">Erro ao gerar matriz.</div>';
    }
}
'''

# Substitui a função
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
    html = html[:idx_inicio] + nova_verificar.strip() + html[i:]
    print("✅ Função 'verificarEGerar()' corrigida para usar o histórico.")
else:
    print("❌ Função 'verificarEGerar()' não encontrada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Arquivo salvo.")
