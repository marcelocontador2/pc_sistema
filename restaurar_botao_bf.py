import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_financeira_bf.html"

shutil.copy2(arquivo, f"{arquivo}.bak_visual_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Cria o HTML do botão perfeito (com cor azul, texto branco e bordas arredondadas)
botao_perfeito = '<button id="btn-pdf-unico" style="background:#3182ce; color:white; padding:8px 16px; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Gerar PDF</button>'

# 2. Substitui o botão fantasma pelo botão perfeito
# Procura qualquer tag (button, a, div) que tenha o texto "Gerar PDF" e substitui
c = re.sub(r'<(?:button|a|div)[^>]*>\s*Gerar PDF\s*<\/(?:button|a|div)>', botao_perfeito, c, flags=re.IGNORECASE)

# 3. Garante que o script de clique (event listener) está no final da página
# Remove versões antigas para não duplicar
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf = document\.getElementById\(\'btn-pdf-unico\'\);.*?</script>', '', c, flags=re.DOTALL)

script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const btnPdf = document.getElementById('btn-pdf-unico');
            
            if (btnPdf) {
                btnPdf.addEventListener('click', function() {
                    const sel = document.querySelector('input[name="historico"]:checked') || document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {
                        alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                        return;
                    }
                    
                    const url = `/gerar_pdf_analise_financeira_bf?historico_id=${sel.value}`;
                    
                    // Técnica da nova aba sem bloqueio de pop-up
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                console.log("[DEBUG] Botão PDF restaurado e clicável!");
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
print("[OK] Botão 'Gerar PDF' restaurado com visual azul e função ativa!")
