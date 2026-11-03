import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_financeira_bf.html"

shutil.copy2(arquivo, f"{arquivo}.bak_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove TODAS as funções de PDF antigas e quebradas
c = re.sub(r'function gerarPDFFinanceiro\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)
c = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)

# 2. Limpa qualquer onclick de PDF existente no HTML
c = re.sub(r'onclick="[^"]*gerarPDF[^"]*"', 'id="btn-pdf-unico"', c, flags=re.IGNORECASE)

# 3. Garante que o botão tem o ID correto (caso o regex acima tenha pulado algum)
# Procura qualquer botão que tenha "Gerar PDF" no texto e adiciona o id
c = re.sub(r'(<button[^>]*>)(.*?Gerar PDF.*?)(</button>)', r'<button class="btn btn-pdf" id="btn-pdf-unico">\2\3', c, flags=re.IGNORECASE)

# 4. Injeta o JavaScript final com o event listener (muito mais seguro)
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const btnPdf = document.getElementById('btn-pdf-unico');
            
            if (btnPdf) {
                // Remove qualquer listener antigo (garantia)
                const novoBtn = btnPdf.cloneNode(true);
                btnPdf.parentNode.replaceChild(novoBtn, btnPdf);
                
                novoBtn.addEventListener('click', function() {
                    console.log("[DEBUG] Botão PDF clicado!");
                    
                    const sel = document.querySelector('input[name="historico"]:checked') || document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {
                        alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                        return;
                    }
                    
                    const url = `/gerar_pdf_analise_financeira_bf?historico_id=${sel.value}`;
                    console.log("[DEBUG] Abrindo PDF:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                
                console.log("[DEBUG] Botão PDF conectado com sucesso!");
            } else {
                console.log("[DEBUG] ERRO: Botão PDF não encontrado.");
            }
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão PDF da Análise Financeira refeito com event listener seguro!")
