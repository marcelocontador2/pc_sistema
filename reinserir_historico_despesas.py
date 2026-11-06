import re, shutil, datetime, os

arq = r"pc_frontend\analise_comparativo_despesas.html"
shutil.copy2(arq, f"{arq}.bak_correcao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Função carregarHistorico que estava faltando (agora com checkbox e loading)
funcao_hist = """async function carregarHistorico() {
            try {
                const res = await fetch(`/historico_comparativo_despesas?_t=${Date.now()}`);
                const data = await res.json();
                const div = document.getElementById('historico-lista');
                if (data.length === 0) {
                    div.innerHTML = '<p style="color:#718096;font-size:13px;">Nenhum histórico.</p>';
                    return;
                }
                let html = '<ul>';
                data.forEach(item => {
                    html += `<li>
                        <input type="checkbox" class="check-historico" value="${item.id}">
                        <span><b>Período:</b> ${item.periodo} | <b>Gerado em:</b> ${item.data_geracao}</span>
                    </li>`;
                });
                html += '</ul>';
                div.innerHTML = html;
            } catch (e) {
                console.error(e);
                document.getElementById('historico-lista').innerHTML = '<p>Erro ao carregar histórico.</p>';
            }
        }"""

# Se a função não existe, injeta antes do "document.addEventListener('DOMContentLoaded'"
if "function carregarHistorico" not in html and "async function carregarHistorico" not in html:
    idx = html.find("document.addEventListener('DOMContentLoaded'")
    if idx == -1:
        idx = html.find("document.addEventListener(\"DOMContentLoaded\"")
    
    if idx != -1:
        html = html[:idx] + funcao_hist + "\n\n        " + html[idx:]
        with open(arq, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Função carregarHistorico reinjetada no arquivo de Despesas.")
    else:
        print("[ERRO] Não encontrei o ponto de injeção (DOMContentLoaded).")
else:
    print("[INFO] A função carregarHistorico já existe. Nada foi alterado.")

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor (só mudou HTML).")
print("2. Aperte Ctrl+Shift+R no navegador na tela de Despesas.")
print("3. O histórico deve carregar normalmente.")
