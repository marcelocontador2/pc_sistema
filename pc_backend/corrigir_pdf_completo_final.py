c = open('../pc_frontend/custo_pessoal_pdf_completo.html', encoding='utf-8-sig').read()
# O novo script completo e mapeado
novo_script = """
    <script>
        function fmt(v) {
            return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        function fmtPct(v) {
            return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';
        }

        const params = new URLSearchParams(window.location.search);
        const periodo = params.get('periodo') || '2026-TRIMESTRE-3';
        const entidade = params.get('entidade') || 'COFEN';

        fetch(`/api/custo_pessoal/${periodo}?entidade=${entidade}&_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                const rclTotal = d.rcl_total || 0;
                const custoTotal = d.custo_total || 0;
                const limiteTotal = d.limite_atual || d.limite_total || 0;
                const margemTotal = d.margem_disponivel_atual || (limiteTotal - custoTotal);
                
                const pctLimiteNum = (d.limite_pct || 0.6) * 100;
                const pctLimiteFmt = pctLimiteNum.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';

                // 1. Tabela de RCL e Limites
                document.getElementById('rcl-atual').innerText = fmt(d.rcl_atual || 0);
                document.getElementById('rcl-anterior').innerText = fmt(d.rcl_anterior || 0);
                document.getElementById('rcl-total').innerText = fmt(rclTotal);
                document.getElementById('limite-total').innerText = fmt(limiteTotal);

                // 2. Tabela de Custos Detalhados
                // Pessoal
                document.getElementById('pessoal-atual').innerText = fmt(d.pessoal_atual || 0);
                document.getElementById('pessoal-anterior').innerText = fmt(d.pessoal_anterior || 0);
                document.getElementById('pessoal-total').innerText = fmt(d.pessoal_total || 0);
                document.getElementById('pessoal-pct').innerText = fmtPct((d.pessoal_total / rclTotal) * 100);

                // RGPS (Outras)
                document.getElementById('rgps-atual').innerText = fmt(d.outras_atual || 0);
                document.getElementById('rgps-anterior').innerText = fmt(d.outras_anterior || 0);
                document.getElementById('rgps-total').innerText = fmt(d.outras_total || 0);
                document.getElementById('rgps-pct').innerText = fmtPct((d.outras_total / rclTotal) * 100);

                // Terceirização
                document.getElementById('terc-atual').innerText = fmt(d.terc_atual || 0);
                document.getElementById('terc-anterior').innerText = fmt(d.terc_anterior || 0);
                document.getElementById('terc-total').innerText = fmt(d.terc_total || 0);
                document.getElementById('terc-pct').innerText = fmtPct((d.terc_total / rclTotal) * 100);

                // Custo Total
                document.getElementById('custo-atual').innerText = fmt(d.custo_atual || 0);
                document.getElementById('custo-anterior').innerText = fmt(d.custo_anterior || 0);
                document.getElementById('custo-total').innerText = fmt(custoTotal);

                // 3. Conclusão
                document.getElementById('pct-limite-texto').innerText = pctLimiteFmt;
                document.getElementById('conclusao-limite').innerText = 'R$ ' + fmt(limiteTotal);
                document.getElementById('conclusao-custo-pct').innerText = fmtPct((custoTotal/rclTotal)*100);
                document.getElementById('conclusao-custo-ajustado').innerText = fmtPct((custoTotal/rclTotal)*100); // Se houver lógica de exclusão de sentenças, aplicar aqui

                // 4. Comparativo Final
                document.getElementById('final-rcl').innerText = fmt(rclTotal);
                document.getElementById('final-custo').innerText = fmt(custoTotal);
                document.getElementById('final-custo-pct').innerText = fmtPct((custoTotal/rclTotal)*100);
                document.getElementById('final-margem').innerText = fmt(margemTotal);
                document.getElementById('final-margem-pct').innerText = fmtPct((margemTotal/rclTotal)*100);
                document.getElementById('final-limite').innerText = fmt(limiteTotal);
                document.getElementById('final-limite-pct').innerText = pctLimiteFmt;

                // 5. Situação
                const situacao = document.getElementById('final-situacao');
                if (custoTotal <= limiteTotal) {
                    situacao.innerText = 'Dentro do limite legal (<= ' + pctLimiteFmt + ')';
                    situacao.className = 'success';
                } else {
                    situacao.innerText = 'Acima do limite legal (> ' + pctLimiteFmt + ')';
                    situacao.className = 'danger';
                }
            })
            .catch(e => {
                console.error(e);
                document.getElementById('final-situacao').innerText = 'Erro ao carregar dados.';
            });
    </script>
</body>
</html>
"""
# Substitui o script antigo pelo novo (do "<script>" até o final do arquivo)
import re
c = re.sub(r'<script>.*?</html>', novo_script, c, flags=re.DOTALL)
open('../pc_frontend/custo_pessoal_pdf_completo.html', 'w', encoding='utf-8').write(c)
print("[OK] JavaScript do PDF Completo atualizado com todos os campos dinâmicos!")
