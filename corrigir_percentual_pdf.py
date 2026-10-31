from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar ID no percentual do limite (linha 87)
trecho_antigo = '<tr><td>Limite Resolução Cofen 814/2026</td><td id="pdf-resumo-limite" class="right">0,00</td><td class="right">50,00%</td></tr>'
trecho_novo = '<tr><td>Limite Resolução Cofen 814/2026</td><td id="pdf-resumo-limite" class="right">0,00</td><td class="right" id="pdf-resumo-limite-pct">50,00%</td></tr>'

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: ID adicionado no percentual do limite (resumo)!")

# 2. Adicionar ID na mensagem "Dentro do limite legal (= 50%)"
trecho_antigo2 = '<tr><td colspan="3" class="center" style="font-weight: bold; color: #28a745;">✅ Dentro do limite legal (= 50%)</td></tr>'
trecho_novo2 = '<tr><td colspan="3" class="center" style="font-weight: bold; color: #28a745;" id="pdf-resumo-status">✅ Dentro do limite legal (= 50%)</td></tr>'

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: ID adicionado na mensagem de status!")

# 3. Atualizar o JS para preencher o percentual e a mensagem
trecho_js = "document.getElementById('pdf-resumo-limite').innerText = fmt(limite);"
if trecho_js in conteudo:
    novo_js = '''document.getElementById('pdf-resumo-limite').innerText = fmt(limite);
                    document.getElementById('pdf-resumo-limite-pct').innerText = (limite_pct * 100).toFixed(2) + '%';
                    var statusEl = document.getElementById('pdf-resumo-status');
                    if (statusEl) {
                        var dentro = custo <= limite;
                        statusEl.innerText = dentro ? '✅ Dentro do limite legal (= ' + (limite_pct * 100).toFixed(2) + '%)' : '❌ Acima do limite legal (= ' + (limite_pct * 100).toFixed(2) + '%)';
                        statusEl.style.color = dentro ? '#28a745' : '#dc3545';
                    }'''
    conteudo = conteudo.replace(trecho_js, novo_js, 1)
    print("OK: JS atualizado para preencher percentual e status!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML do PDF completo atualizado!")
