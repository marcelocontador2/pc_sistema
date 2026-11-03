import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_financeira_bf.html"

shutil.copy2(arquivo, f"{arquivo}.bak_checkbox_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove a versão antiga do script de clique
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf = document\.getElementById\(\'btn-pdf-unico\'\);.*?</script>', '', c, flags=re.DOTALL)

# Novo script que aceita CHECKBOX e RADIO
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const btnPdf = document.getElementById('btn-pdf-unico');
            
            if (btnPdf) {
                btnPdf.addEventListener('click', function() {
                    // Procura QUALQUER checkbox ou radio marcado na tela
                    const sel = document.querySelector('input[type="checkbox"]:checked') || 
                                document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {
                        alert("Atenção: Selecione um item do Histórico Salvo (marque a caixinha) antes de gerar o PDF.");
                        return;
                    }
                    
                    // Se o input tiver um value, usa. Se não, pega o ID do elemento pai.
                    let id = sel.value;
                    if (!id || id === "on") {
                        id = sel.id.replace('check-', '').replace('hist-', '');
                        if (!id) id = sel.getAttribute('data-id');
                    }
                    
                    const url = `/gerar_pdf_analise_financeira_bf?historico_id=${id}`;
                    console.log("[DEBUG] Abrindo PDF com ID:", id);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                console.log("[DEBUG] Botão PDF configurado para aceitar Checkbox e Radio!");
            }
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Script do botão PDF atualizado para aceitar Checkbox!")
