c = open('../pc_frontend/custo_pessoal_pdf_completo.html', encoding='utf-8-sig').read()

antigo_js = """
                const situacao = document.getElementById('final-situacao');
                const pctCusto = (custoTotal / rclTotal) * 100;
                const isCoren = (entidade.toUpperCase() === 'COREN');
                
                let statusTexto = '';
                let statusClasse = '';

                // Lógica baseada nas Faixas de Controle do Art. 6º
                if (isCoren) {
                    if (pctCusto > 60) { statusTexto = 'Faixa Crítica (> 60%)'; statusClasse = 'danger'; }
                    else if (pctCusto >= 57) { statusTexto = 'Faixa Prudencial (57% a 60%)'; statusClasse = 'warning'; }
                    else if (pctCusto >= 54) { statusTexto = 'Faixa de Alerta (54% a 57%)'; statusClasse = 'warning'; }
                    else { statusTexto = 'Abaixo da Faixa de Alerta (Saudável)'; statusClasse = 'success'; }
                } else { // COFEN
                    if (pctCusto > 50) { statusTexto = 'Faixa Crítica (> 50%)'; statusClasse = 'danger'; }
                    else if (pctCusto >= 47.5) { statusTexto = 'Faixa Prudencial (47,5% a 50%)'; statusClasse = 'warning'; }
                    else if (pctCusto >= 45) { statusTexto = 'Faixa de Alerta (45% a 47,5%)'; statusClasse = 'warning'; }
                    else { statusTexto = 'Abaixo da Faixa de Alerta (Saudável)'; statusClasse = 'success'; }
                }

                situacao.innerText = statusTexto;
                situacao.className = statusClasse;
"""

novo_js = """
                const situacao = document.getElementById('final-situacao');
                // Puxa a regra de negócio direto do backend
                situacao.innerText = d.faixa_controle || 'Abaixo da Faixa de Alerta (Saudável)';
                situacao.className = d.faixa_cor || 'success';
"""

if antigo_js in c:
    c = c.replace(antigo_js, novo_js)
    print("[OK] PDF atualizado para consumir a faixa do backend!")
else:
    # Fallback simples caso os espaços tenham mudado
    c = re.sub(r'const situacao = document\.getElementById\(\'final-situacao\'\);.*?situacao\.className = statusClasse;', novo_js, c, flags=re.DOTALL)
    print("[OK] PDF atualizado via Regex!")

open('../pc_frontend/custo_pessoal_pdf_completo.html', 'w', encoding='utf-8').write(c)
