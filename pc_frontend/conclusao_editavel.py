c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# 1. Torna os parágrafos da conclusão editáveis
c = c.replace(
    '<p id="conclusao-total" style="font-size: 14px; line-height: 1.6;">',
    '<p id="conclusao-total" contenteditable="true" style="font-size: 14px; line-height: 1.6; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">'
)
c = c.replace(
    '<p id="conclusao-concentracao" style="font-size: 14px; line-height: 1.6;">',
    '<p id="conclusao-concentracao" contenteditable="true" style="font-size: 14px; line-height: 1.6; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">'
)
c = c.replace(
    '<ul id="conclusao-alertas" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;">',
    '<ul id="conclusao-alertas" contenteditable="true" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">'
)
c = c.replace(
    '<ul id="conclusao-recomendacoes" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;">',
    '<ul id="conclusao-recomendacoes" contenteditable="true" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">'
)

# 2. Adiciona um botão "Salvar Edição" no final da página de conclusão
if "Salvar Edição" not in c:
    c = c.replace(
        "</div>\n    </div>\n</body>",
        "</div>\n        <div style='text-align: right; margin-top: 20px;'>\n            <button onclick='salvarEdicao()' style='padding: 10px 20px; background: var(--primary); color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;'>💾 Salvar Edição</button>\n        </div>\n    </div>\n</body>"
    )

# 3. Adiciona a função salvarEdicao no JavaScript
if "function salvarEdicao" not in c:
    script_salvar = """
        function salvarEdicao() {
            // Pega os textos editados
            const total = document.getElementById('conclusao-total').innerHTML;
            const concentracao = document.getElementById('conclusao-concentracao').innerHTML;
            const alertas = document.getElementById('conclusao-alertas').innerHTML;
            const recomendacoes = document.getElementById('conclusao-recomendacoes').innerHTML;
            
            // Salva no localStorage para persistir
            localStorage.setItem('relatorio_conclusao', JSON.stringify({
                total: total,
                concentracao: concentracao,
                alertas: alertas,
                recomendacoes: recomendacoes
            }));
            
            alert('Edição salva com sucesso!');
        }
        
        // Carrega as edições salvas ao iniciar
        window.addEventListener('load', function() {
            const saved = localStorage.getItem('relatorio_conclusao');
            if (saved) {
                const dados = JSON.parse(saved);
                if (dados.total) document.getElementById('conclusao-total').innerHTML = dados.total;
                if (dados.concentracao) document.getElementById('conclusao-concentracao').innerHTML = dados.concentracao;
                if (dados.alertas) document.getElementById('conclusao-alertas').innerHTML = dados.alertas;
                if (dados.recomendacoes) document.getElementById('conclusao-recomendacoes').innerHTML = dados.recomendacoes;
            }
        });
    """
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + script_salvar + "\n" + c[pos:]

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Conclusão editável e botão de salvar adicionados!")
