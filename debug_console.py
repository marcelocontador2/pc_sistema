import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_debug_console")

# Substitui a função verificar por uma versão com logs detalhados
nova_verificar = '''
function verificar() {
    console.log("[DEBUG] verificar() chamada");
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo').value;
    const valor = document.getElementById('valor').value;
    const periodo = `${ano}-${tipo}-${valor}`;
    console.log("[DEBUG] periodo:", periodo);

    const container = document.getElementById('tabela-container');
    container.innerHTML = '<div class="loading">Buscando dados...</div>';

    fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`)
        .then(res => {
            console.log("[DEBUG] HTTP status:", res.status);
            if (!res.ok) {
                throw new Error("HTTP " + res.status);
            }
            return res.json();
        })
        .then(data => {
            console.log("[DEBUG] data recebida:", data);
            if (data.erro) {
                alert("Aviso: " + data.mensagem);
                container.innerHTML = '';
                return;
            }
            try {
                atualizarCards(data);
                console.log("[DEBUG] cards atualizados");
                renderizarTabela(data);
                console.log("[DEBUG] tabela renderizada");
            } catch (e) {
                console.error("[DEBUG] ERRO na renderização:", e);
                container.innerHTML = '<div class="loading">Erro ao renderizar: ' + e.message + '</div>';
            }
        })
        .catch(err => {
            console.error("[DEBUG] ERRO no fetch:", err);
            container.innerHTML = '<div class="loading">Erro na comunicação: ' + err.message + '</div>';
        });
}
'''

# Localiza e substitui a função verificar
idx_inicio = html.find("function verificar()")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_verificar.strip() + html[i:]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função verificar() substituída com logs de debug.")
else:
    print("❌ Função verificar() não encontrada.")

# Força o navegador a não usar cache adicionando um query string nas referências de CSS/JS
# (mas como o JS é inline, o cache é do HTML em si)
