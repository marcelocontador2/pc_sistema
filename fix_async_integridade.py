import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_async_integridade")

# 1. Verifica se a função verificarMatriz usa await
if "async function verificarMatriz" in html:
    print("✅ Função 'verificarMatriz' já é async. O problema pode ser outro.")
elif "function verificarMatriz" in html and "await" in html:
    print("⚠️ Função 'verificarMatriz' usa await mas não é async. Corrigindo...")
    html = html.replace("function verificarMatriz(", "async function verificarMatriz(")
    print("✅ Adicionado 'async' na função verificarMatriz.")

# 2. Procura por outras funções que usam await sem ser async
funcoes_com_await = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*await', html, re.DOTALL)
for func in funcoes_com_await:
    if f"async function {func}" not in html:
        print(f"⚠️ Função '{func}' usa await mas não é async. Adicionando 'async'...")
        html = re.sub(
            rf'function\s+{func}\s*\(([^)]*)\)\s*\{{',
            rf'async function {func}(\1) {{',
            html,
            count=1
        )

# 3. Se a função verificarMatriz não existir, cria uma versão simples
if "function verificarMatriz" not in html and "async function verificarMatriz" not in html:
    print("⚠️ Função 'verificarMatriz' não existe. Criando uma nova...")
    nova_funcao = '''
async function verificarMatriz() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo').value;
    const trimestre = document.getElementById('trimestre').value;
    const periodo = `${ano}-${tipo}-${trimestre}`;

    const container = document.getElementById('matriz-container');
    if (container) container.innerHTML = '<div class="loading">Buscando dados...</div>';

    try {
        const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
        const data = await res.json();

        if (data.erro) {
            alert("Aviso: " + data.mensagem);
            if (container) container.innerHTML = '';
            return;
        }

        // Renderiza a matriz
        if (container) {
            let html = '<table class="data-table"><thead><tr><th>Descrição</th><th>Valor</th><th>Consistente?</th><th>Observação</th></tr></thead><tbody>';
            (data.matriz || []).forEach(m => {
                html += `<tr>
                    <td>${m.descricao}</td>
                    <td class="text-right">${formatarMoeda(m.valor_bp || m.valor_bo || m.valor_bf || m.valor_dvp || 0)}</td>
                    <td>${m.consistente ? '✅' : '❌'}</td>
                    <td>${m.observacao || ''}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
    } catch (err) {
        console.error(err);
        if (container) container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
    }
}
'''
    html = html.replace("</script>", nova_funcao + "\n</script>")
    print("✅ Função 'verificarMatriz' criada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Arquivo HTML de integridade salvo.")
