import shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')

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

        /* GRID DE CARDS */
        .cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; flex: 1; }
        .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; position: relative; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); display: flex; flex-direction: column; justify-content: center; }
        .card::before { content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 100%; border-top-left-radius: 12px; border-bottom-left-radius: 12px; background: #3182ce; }
        .card.verde::before { background: #10b981; }
        .card.vermelho::before { background: #ef4444; }
        .card.azul::before { background: #3b82f6; }
        .card.roxo::before { background: #8b5cf6; }
        .card.laranja::before { background: #f59e0b; }

        .card-title { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; line-height: 1.4; }
        .card-value { font-size: 32px; font-weight: 700; color: #0f172a; }
        .card.verde .card-value { color: #10b981; }
        .card.vermelho .card-value { color: #ef4444; }

        /* RODAPÉ */
        .footer { margin-top: 30px; display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px; }
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

        <div class="cards-grid" id="cards-container">
            <!-- Injetados via JS -->
        </div>

        <div class="footer">
            <div>SGPC - Sistema de Gestão de Prestação de Contas</div>
            <div>Documento Confidencial - Uso Exclusivo da Diretoria</div>
        </div>
    </div>

    <script>
        function resumido(v) {
            if (!v) return "R$ 0,0 mi";
            const num = Number(v) / 1000000;
            return (num < 0 ? "-R$ " : "R$ ") + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }

        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            document.getElementById("data-emissao").innerText = new Date().toLocaleDateString('pt-BR');

            if (!historicoId) return;

            try {
                // 1. Busca o período no Histórico
                const resHist = await fetch(`/historico_panorama/${historicoId}`);
                const histData = await resHist.json();
                const periodo = histData.periodo || "2026-TRIMESTRE-3";

                document.getElementById("periodo-titulo").innerText = periodo;

                // 2. Busca os valores CORRETOS na rota que a tela usa (/api/panorama/)
                const resApi = await fetch(`/api/panorama/${periodo}`);
                const d = await resApi.json();

                // 3. Extrai os valores garantindo as chaves certas do JSON
                const caixa = d.caixa_bp || 0;
                const ativo = d.ativo_total || 0;
                const passivo = d.passivo_total || 0; // Agora ele lê o passivo puro
                const pl = d.patrimonio_liquido || 0;
                const receita = d.receita_realizada || 0;
                const despesa = d.despesa_empenhada || 0;
                
                const resOrc = d.superavit_orcamentario || 0;
                const resPat = d.superavit_patrimonial || 0;
                const resFin = d.superavit_financeiro || 0;

                // Cores e Títulos dinâmicos
                const corOrc = resOrc < 0 ? "vermelho" : "verde";
                const corPat = resPat < 0 ? "vermelho" : "verde";
                const corFin = resFin < 0 ? "vermelho" : "verde";
                
                const tituloOrc = resOrc < 0 ? "Déficit Orçamentário" : "Superávit Orçamentário";
                const tituloPat = resPat < 0 ? "Déficit Patrimonial (DVP)" : "Superávit Patrimonial (DVP)";
                const tituloFin = resFin < 0 ? "Déficit Financeiro (BP)" : "Superávit Financeiro (BP)";

                let html = `
                    <div class="card azul">
                        <div class="card-title">Caixa e Equivalente de Caixa (BP)</div>
                        <div class="card-value">${resumido(caixa)}</div>
                    </div>
                    <div class="card roxo">
                        <div class="card-title">Ativo Total (BP)</div>
                        <div class="card-value">${resumido(ativo)}</div>
                    </div>
                    <div class="card roxo">
                        <div class="card-title">Passivo Total (BP)</div>
                        <div class="card-value">${resumido(passivo)}</div>
                    </div>
                    <div class="card roxo">
                        <div class="card-title">Patrimônio Líquido (BP)</div>
                        <div class="card-value">${resumido(pl)}</div>
                    </div>
                    <div class="card verde">
                        <div class="card-title">Receitas Realizadas (BO)</div>
                        <div class="card-value">${resumido(receita)}</div>
                    </div>
                    <div class="card vermelho">
                        <div class="card-title">Despesas Empenhadas (BO)</div>
                        <div class="card-value">${resumido(despesa)}</div>
                    </div>
                    <div class="card ${corOrc}">
                        <div class="card-title">${tituloOrc}</div>
                        <div class="card-value">${resumido(resOrc)}</div>
                    </div>
                    <div class="card ${corPat}">
                        <div class="card-title">${tituloPat}</div>
                        <div class="card-value">${resumido(resPat)}</div>
                    </div>
                    <div class="card ${corFin}">
                        <div class="card-title">${tituloFin}</div>
                        <div class="card-value">${resumido(resFin)}</div>
                    </div>
                `;

                document.getElementById("cards-container").innerHTML = html;

            } catch (e) {
                console.error("Erro ao carregar dados:", e);
                document.getElementById("cards-container").innerHTML = "<p style='color:red;'>Erro ao carregar os dados.</p>";
            }
        });
    </script>
</body>
</html>"""

with open(r"pc_frontend\relatorio_panorama.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("[OK] Relatório refeito: Puxando valores da API e com Passivo correto!")
