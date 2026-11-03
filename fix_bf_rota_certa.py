import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_financeira_bf.html"

shutil.copy2(arquivo, f"{arquivo}.bak_rota_certa_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove a versão antiga do script de clique
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf = document\.getElementById\(\'btn-pdf-unico\'\);.*?</script>', '', c, flags=re.DOTALL)

# Novo script ajustado para a rota correta: /gerar_pdf_analise_financeira_bf/{id}
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const btnPdf = document.getElementById('btn-pdf-unico');
            
            if (btnPdf) {
                btnPdf.addEventListener('click', function() {
                    const sel = document.querySelector('input[type="checkbox"]:checked') || 
                                document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {
                        alert("Atenção: Selecione um item do Histórico Salvo (marque a caixinha) antes de gerar o PDF.");
                        return;
                    }
                    
                    let id = sel.value;
                    if (!id || id === "on") {
                        id = sel.id.replace('check-', '').replace('hist-', '');
                        if (!id) id = sel.getAttribute('data-id');
                    }
                    
                    // ROTA CORRETA: O ID vai no path da URL, não como query string
                    const url = `/gerar_pdf_analise_financeira_bf/${id}`;
                    console.log("[DEBUG] Abrindo PDF com ID no path:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                console.log("[DEBUG] Botão PDF configurado para a rota correta!");
            }
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão PDF corrigido para chamar /gerar_pdf_analise_financeira_bf/{id}")
