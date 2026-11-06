import re, shutil, datetime

arquivo = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arquivo, f"{arquivo}.bak_exibir_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Encontra e substitui a função exibirSelecionado
padrao = re.compile(r'async function exibirSelecionado\(\)\s*\{.*?\n        \}', re.DOTALL)

nova_func = """async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico."); return; }
            
            try {
                const res = await fetch(`/historico_relatorio_consolidado/${check.value}`);
                const data = await res.json();
                if (data.erro) { alert("Erro ao carregar histórico."); return; }
                
                const statusArea = document.getElementById('status-area');
                const modulosArea = document.getElementById('modulos-area');
                
                // Garante que pega o período e a data, mesmo se vier em formato diferente
                const periodo = data.periodo || data.periodo_atual || "N/A";
                const dataGeracao = data.data_geracao || data.data || "N/A";
                
                statusArea.innerHTML = `<div class="status-box status-ok">
                    <strong>✓ Histórico carregado!</strong>
                    <p>Período ${periodo} (salvo em ${dataGeracao})</p>
                </div>`;
                
                let html = '<h3>Módulos Consolidados:</h3>';
                
                // O JSON do banco tem a chave "dados", e dentro dela os módulos.
                // Se não tiver, tenta ler direto do objeto raiz.
                let modulos = data.dados ? (data.dados.dados ? data.dados.dados : data.dados) : data;
                
                let encontrouAlgum = false;
                for (const chave in modulos) {
                    if (chave === 'periodo' || chave === 'data_geracao' || chave === 'erro') continue; 
                    
                    const m = modulos[chave];
                    if (m && m.nome) {
                        html += `<div class="modulo-item"><span>${m.nome}</span><span class="modulo-ok">✓ ${m.data_geracao || ''}</span></div>`;
                        encontrouAlgum = true;
                    }
                }
                
                if (!encontrouAlgum) {
                    html += '<p style="color:#666;">Nenhum módulo listado no histórico.</p>';
                }
                
                modulosArea.innerHTML = html;
            } catch(e) {
                console.error("Erro ao exibir:", e);
                alert("Erro de conexão ao exibir histórico.");
            }
        }"""

if padrao.search(html):
    html = padrao.sub(nova_func, html)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Função exibirSelecionado corrigida.")
else:
    print("[AVISO] Função não encontrada no arquivo.")

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione o histórico e clique em Exibir.")
