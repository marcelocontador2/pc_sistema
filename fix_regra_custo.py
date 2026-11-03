import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_custo_pessoal.html"

shutil.copy2(arquivo, f"{arquivo}.bak_custo_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove os onclick antigos do(s) botão(ões) de PDF
c = re.sub(r'onclick="gerarPDFHistorico\(\)"', '', c)
c = re.sub(r'onclick="gerarPDF\(\)"', '', c)
c = re.sub(r'onclick="window\.open\([^)]*gerar_pdf[^)]*\)"', '', c)

# 2. Adiciona um ID único ao botão de PDF (se houver mais de um, tratamos pelo texto)
c = re.sub(r'(<button[^>]*?>[^<]*?Gerar PDF[^<]*?</button>)', r'\1', c) # Apenas garante que o botão está limpo

# 3. Injeta a nova regra de negócio no final da página
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Procura todos os botões que têm "PDF" no texto
            const botoes = Array.from(document.querySelectorAll('button'));
            const botoesPDF = botoes.filter(b => b.innerText.toUpperCase().includes('PDF'));

            botoesPDF.forEach(function(btn) {
                // Clona o botão para destruir qualquer evento antigo que tenha ficado preso
                const novoBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(novoBtn, btn);

                // Adiciona o novo evento com a regra de negócio
                novoBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Verifica se alguma caixinha de histórico está marcada
                    const check = document.querySelector('.check-historico:checked');
                    if (!check) {
                        alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                        return;
                    }
                    
                    // Verifica qual botão foi clicado para escolher a rota correta
                    const texto = novoBtn.innerText.toUpperCase();
                    let rota = '';
                    
                    if (texto.includes('COMPLETO')) {
                        rota = '/gerar_pdf_completo_custo_pessoal';
                    } else {
                        rota = '/gerar_pdf_custo_pessoal';
                    }
                    
                    const url = `${rota}?id=${check.value}`;
                    console.log("[DEBUG] Abrindo PDF Custo Pessoal:", url);
                    window.open(url, '_blank');
                });
            });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Regra de negócio aplicada no Custo de Pessoal com sucesso!")
