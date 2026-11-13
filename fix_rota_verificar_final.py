import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_verificar_final")

# Encontra e substitui a função verificarEGerar
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
    
    # Nova função robusta: busca os dados para exibir na tela e avisa se der erro
    nova_verificar = '''async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Buscando dados da matriz...</div>';

        try {
            // Busca direto da rota de geração
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            
            if (!res.ok) {
                throw new Error(`Erro na requisição: Status ${res.status}`);
            }

            const data = await res.json();

            if (data.erro) {
                if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">Erro do Backend: ${data.mensagem}</div>`;
                return;
            }

            // Se a resposta for vazia ou não tiver matriz
            if (!data.matriz || data.matriz.length === 0) {
                if (container) container.innerHTML = '<div style="padding: 20px;">Nenhum dado retornado pela API para este período.</div>';
                return;
            }

            dadosAtuais = data;
            // Renderiza usando a mesma função do layout azul
            renderizarMatriz(data, container);

        } catch (err) {
            console.error("Erro completo:", err);
            if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">
                <strong>Falha ao buscar dados.</strong><br>
                Verifique se a rota GET <code>/api/integridade_matriz/${periodo}</code> está funcionando no seu backend.<br>
                Erro: ${err.message}
            </div>`;
        }
    }'''

    html = html[:idx_inicio] + nova_verificar + html[i:]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'verificarEGerar' reescrita para buscar os dados na rota GET e exibir erros na tela!")
else:
    print("❌ Função 'verificarEGerar' não encontrada no arquivo.")
