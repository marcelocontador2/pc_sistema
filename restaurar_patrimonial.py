import os, glob, shutil, re

# 1. Encontra o backup mais recente e restaura o HTML original
backups = glob.glob(r"pc_frontend\analise_patrimonial.html.bak_patrim_*")
if backups:
    backups.sort(reverse=True)
    ultimo_backup = backups[0]
    shutil.copy2(ultimo_backup, r"pc_frontend\analise_patrimonial.html")
    print(f"[OK] Layout restaurado a partir do backup: {ultimo_backup}")
else:
    print("[AVISO] Backup não encontrado. O layout precisará ser recriado manualmente.")

# 2. Abre o HTML restaurado
arquivo = r"pc_frontend\analise_patrimonial.html"
c = open(arquivo, encoding='utf-8').read()

# 3. Remove qualquer resquício de script antigo quebrado
c = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf = document\.getElementById\(\'btn-pdf-unico\'\);.*?</script>', '', c, flags=re.DOTALL)

# 4. Injeta o JavaScript inteligente (Ele acha o botão no HTML, estiliza e adiciona o clique)
script_seguro = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Procura qualquer botão na tela que tenha o texto "Gerar PDF"
            const botoes = Array.from(document.querySelectorAll('button, a'));
            const btnPdf = botoes.find(b => b.innerText.includes('Gerar PDF'));
            
            if (btnPdf) {
                // Garante o visual azul (caso o backup estivesse sem estilo)
                btnPdf.style.background = '#3182ce';
                btnPdf.style.color = 'white';
                btnPdf.style.padding = '8px 16px';
                btnPdf.style.border = 'none';
                btnPdf.style.borderRadius = '4px';
                btnPdf.style.fontWeight = 'bold';
                btnPdf.style.cursor = 'pointer';
                
                // Remove o clique antigo quebrado
                btnPdf.removeAttribute('onclick');
                
                // Adiciona a regra de negócio correta
                btnPdf.addEventListener('click', function(e) {
                    e.preventDefault();
                    
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
                    
                    const url = `/gerar_pdf_analise_patrimonial/${id}`;
                    console.log("[DEBUG] Abrindo PDF Patrimonial via JS:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
            }
        });
    </script>
"""

# 5. Insere o script no final da página
if '</body>' in c:
    c = c.replace('</body>', script_seguro + '\n</body>', 1)
else:
    c += script_seguro

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Menu restaurado e botão PDF blindado via JavaScript (sem quebrar o layout)!")
