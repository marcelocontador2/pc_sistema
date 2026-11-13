import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_rota_get")

# Encontra a função
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
    
    # Nova função usando a rota GET que comprovadamente existe
    nova_verificar = '''async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Buscando dados da matriz...</div>';

        try {
            // Usa a rota GET que já sabemos que existe no seu backend
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            
            if (!res.ok) {
                throw new Error(`A rota retornou status ${res.status} (Não encontrada ou erro interno).`);
            }

            const data = await res.json();
            console.log("Dados recebidos do backend:", data); // Ajuda a depurar no F12

            if (data.erro) {
                if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">Erro do Backend: ${data.mensagem}</div>`;
                return;
            }

            dadosAtuais = data;
            // Renderiza com o layout azul que já restauramos
            renderizarMatriz(data, container);

        } catch (err) {
            console.error(err);
            if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">
                <strong>Falha ao buscar dados da matriz.</strong><br>
                <small>Erro técnico: ${err.message}</small>
            </div>`;
        }
    }'''

    html = html[:idx_inicio] + nova_verificar + html[i:]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'verificarEGerar' revertida para usar a rota GET!")
