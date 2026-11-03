import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. NOVO RELATÓRIO EXECUTIVO (SEM DEPENDER DE INTERNET)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        @page { size: A4 landscape; margin: 0; }
        * { box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #ffffff;
            margin: 0;
            padding: 0;
            color: #1e293b;
            -webkit-print-color-adjust: exact;
        }

        .page { width: 297mm; height: 210mm; padding: 20mm; display: flex; flex-direction: column; }

        /* CABEÇALHO CORPORATIVO */
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #0f172a; padding-bottom: 15px; margin-bottom: 30px; }
        .header-left h1 { margin: 0; font-size: 32px; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; }
        .header-left p { margin: 5px 0 0 0; font-size: 16px; color: #64748b; }
        .header-right { text-align: right; }
        .header-right .periodo { font-size: 18px; font-weight: 700; color: #0f172a; }
        .header-right .data { font-size: 12px; color: #64748b; margin-top: 5px; }

        /* CARDS DE KPI */
        .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .kpi-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; position: relative; overflow: hidden; }
        .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 5px; height: 100%; background: #0f172a; }
        .kpi-card.verde::before { background: #10b981; }
        .kpi-card.vermelho::before { background: #ef4444; }
        .kpi-card.dourado::before { background: #f59e0b; }
        .kpi-title { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }
        .kpi-value { font-size: 28px; font-weight: 700; color: #0f172a; }

        /* GRÁFICO CSS */
        .chart-area { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 30px; flex: 1; display: flex; flex-direction: column; justify-content: flex-end; gap: 20px; }
        .bar-group { display: flex; align-items: center; gap: 15px; }
        .bar-label { width: 150px; font-size: 14px; font-weight: 600; color: #334155; text-align: right; }
        .bar-container { flex: 1; background: #f1f5f9; height: 40px; border-radius: 6px; overflow: hidden; }
        .bar-fill { height: 100%; display: flex; align-items: center; padding-left: 15px; color: white; font-weight: 700; font-size: 14px; }
        .bar-receita { background: #10b981; }
        .bar-despesa { background: #ef4444; }

        /* RODAPÉ */
        .footer { margin-top: 20px; display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <div class="header-left">
                <h1>Relatório Executivo</h1>
                <p>Panorama de Resultados Contábeis e Orçamentários</p>
            </div>
            <div class="header-right">
                <div class="periodo" id="periodo-titulo">Carregando...</div>
                <div class="data">Emissão: <span id="data-emissao"></span></div>
            </div>
        </div>

        <div class="kpi-grid" id="kpis-topo">
            <div class="kpi-card"><div class="kpi-title">Ativo Total (BP)</div><div class="kpi-value" id="v-ativo">R$ 0</div></div>
            <div class="kpi-card"><div class="kpi-title">Passivo Total (BP)</div><div class="kpi-value" id="v-passivo">R$ 0</div></div>
            <div class="kpi-card"><div class="kpi-title">Patrimônio Líquido</div><div class="kpi-value" id="v-pl">R$ 0</div></div>
        </div>

        <div style="display: flex; gap: 20px; flex: 1;">
            <div style="flex: 1; display: flex; flex-direction: column; gap: 15px;">
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Orçamentário</div>
                    <div class="kpi-value" id="res-orcamentario">R$ 0</div>
                </div>
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Patrimonial</div>
                    <div class="kpi-value" id="res-patrimonial">R$ 0</div>
                </div>
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Financeiro</div>
                    <div class="kpi-value" id="res-financeiro">R$ 0</div>
                </div>
            </div>
            
            <div class="chart-area">
                <div style="font-size: 14px; font-weight: bold; color: #0f172a; margin-bottom: 10px;">Comparativo Realizado (Receitas x Despesas)</div>
                <div class="bar-group">
                    <div class="bar-label">Receitas</div>
                    <div class="bar-container"><div class="bar-fill bar-receita" id="bar-receita" style="width: 0%;">R$ 0</div></div>
                </div>
                <div class="bar-group">
                    <div class="bar-label">Despesas</div>
                    <div class="bar-container"><div class="bar-fill bar-despesa" id="bar-despesa" style="width: 0%;">R$ 0</div></div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>SGPC - Sistema de Gestão de Prestação de Contas</div>
            <div>Documento Confidencial - Uso Exclusivo da Diretoria</div>
        </div>
    </div>

    <script>
        function resumido(v) {
            if (!v) return "R$ 0 mi";
            const num = Number(v) / 1000000;
            return (num < 0 ? "-R$ " : "R$ ") + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }

        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            document.getElementById("data-emissao").innerText = new Date().toLocaleDateString('pt-BR');

            if (!historicoId) return;

            try {
                const res = await fetch(`/historico_panorama/${historicoId}`);
                const data = await res.json();
                
                // A MÁGICA AQUI: Pega os dados independentemente de virem dentro de "dados" ou não
                const d = data.dados ? data.dados : data;

                document.getElementById("periodo-titulo").innerText = data.periodo || "Período";

                // Preenche os valores de cima
                document.getElementById("v-ativo").innerText = resumido(d.ativo_total);
                document.getElementById("v-passivo").innerText = resumido(d.passivo_total);
                document.getElementById("v-pl").innerText = resumido(d.patrimonio_liquido);

                // Preenche os resultados de baixo com cores dinâmicas
                const orc = d.superavit_orcamentario || 0;
                const pat = d.superavit_patrimonial || 0;
                const fin = d.superavit_financeiro || 0;

                const elOrc = document.getElementById("res-orcamentario");
                elOrc.innerText = resumido(orc);
                elOrc.style.color = orc < 0 ? "#ef4444" : "#10b981";

                const elPat = document.getElementById("res-patrimonial");
                elPat.innerText = resumido(pat);
                elPat.style.color = pat < 0 ? "#ef4444" : "#10b981";

                const elFin = document.getElementById("res-financeiro");
                elFin.innerText = resumido(fin);
                elFin.style.color = fin < 0 ? "#ef4444" : "#10b981";

                // Monta o gráfico de barras via CSS
                const receita = d.receita_realizada || 0;
                const despesa = d.despesa_empenhada || 0;
                const maxVal = Math.max(receita, despesa, 1); // Evita divisão por zero

                const pctReceita = (receita / maxVal) * 100;
                const pctDespesa = (despesa / maxVal) * 100;

                const barReceita = document.getElementById("bar-receita");
                barReceita.style.width = pctReceita + "%";
                barReceita.innerText = resumido(receita);

                const barDespesa = document.getElementById("bar-despesa");
                barDespesa.style.width = pctDespesa + "%";
                barDespesa.innerText = resumido(despesa);

            } catch (e) {
                console.error("Erro:", e);
            }
        });
    </script>
</body>
</html>"""

with open(r"pc_frontend\relatorio_panorama.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("[OK] Relatório Executivo com gráfico CSS (imune a bloqueios) criado!")

# ==========================================
# 2. MATAR O DUPLO CLIQUE (DUAS ABAS) NA FORÇA
# ==========================================
front_path = r"pc_frontend\panorama.html"
shutil.copy2(front_path, f"{front_path}.bak_2abas_{ts}")
c = open(front_path, encoding='utf-8').read()

# Remove qualquer resquício de onclick="gerarPDF()" do HTML
c = re.sub(r'onclick="gerarPDF\(\)"', '', c)

# Remove scripts antigos de clique que possam ter ficado
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const botoes = Array\.from.*?</script>', '', c, flags=re.DOTALL)

# Adiciona a blindagem final (clona o botão para destruir eventos antigos)
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const botoes = Array.from(document.querySelectorAll('button, a, div'));
            const btnPdf = botoes.find(b => b.innerText.trim().toUpperCase().includes('GERAR PDF'));
            
            if (btnPdf) {
                // Clona o botão (isso destrói qualquer evento duplicado acoplado nele)
                const novoBtn = btnPdf.cloneNode(true);
                btnPdf.parentNode.replaceChild(novoBtn, btnPdf);
                
                // Adiciona apenas um único evento de clique
                novoBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const check = document.querySelector(".check-historico:checked");
                    if (!check) { 
                        alert("Atenção: Marque um relatório no histórico antes de gerar o PDF."); 
                        return; 
                    }
                    
                    const url = `/gerar_pdf_panorama/${check.value}`;
                    window.open(url, '_blank');
                });
            }
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(front_path, 'w', encoding='utf-8').write(c)
print("[OK] Botão PDF corrigido definitivamente (uma única aba)!")

# ==========================================
# 3. GARANTIR ROTA CORRETA NO MAIN.PY
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_2abas_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Substitui à força qualquer URL antiga do Playwright
c_back = c_back.replace(
    'http://127.0.0.1:9994/panorama?historico_id={historico_id}',
    'http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}'
)

open(back_path, 'w', encoding='utf-8').write(c_back)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
