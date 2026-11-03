import re, shutil, datetime

arquivo = 'analise_comparativo_receitas.html'
shutil.copy2(arquivo, f"{arquivo}.bak_pdf_hist_{datetime.datetime.now().strftime('%H%M%S')}")
c = open(arquivo, encoding='utf-8').read()

# Encontra a função gerarPDF atual e substitui pela versão inteligente
padrao = r'function gerarPDF\(\) \{.*?\n        \}'
nova_funcao = """function gerarPDF() {
            const sel = document.querySelector('input[name="historico"]:checked');
            let periodo = "";
            
            // Se houver um histórico selecionado, extrai o período dele
            if (sel) {
                const spanText = sel.nextElementSibling.innerText;
                const match = spanText.match(/Período:\\s*([^|]+)/);
                if (match) {
                    periodo = match[1].trim();
                }
            }
            
            // Se não houver histórico selecionado, pega dos selects do topo
            if (!periodo) {
                const ano = document.getElementById('ano').value;
                const tipo = document.getElementById('tipo').value;
                const valor = document.getElementById('valor').value;
                periodo = `${ano}-${tipo}-${valor}`;
            }
            
            // Abre a rota do backend passando o período correto
            window.open(`/gerar_pdf_comparativo_receitas?periodo_atual=${periodo}`, '_blank');
        }"""
        
c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Gerar PDF' agora respeita o histórico selecionado!")
