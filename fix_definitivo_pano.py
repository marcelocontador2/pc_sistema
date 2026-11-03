import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. NOVO VISUAL PREMIUM DO PDF (HTML)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        
        @page { size: A4 landscape; margin: 0; }
        
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #f8fafc;
            margin: 0;
            padding: 40px;
            color: #0f172a;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #1e3a8a, #3b82f6);
            padding: 30px 40px;
            border-radius: 12px;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
        }

        .header-left h1 {
            margin: 0;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .header-left p {
            margin: 5px 0 0 0;
            font-size: 16px;
            font-weight: 600;
            opacity: 0.9;
        }

        .header-right {
            text-align: right;
            font-size: 14px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
        }

        .card-title {
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }

        .card-value {
            font-size: 34px;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
            line-height: 1;
        }

        .card.positive { border-left: 6px solid #10b981; }
        .card.positive .card-value { color: #059669; }

        .card.negative { border-left: 6px solid #ef4444; }
        .card.negative .card-value { color: #dc2626; }
        
        .card.neutral { border-left: 6px solid #6366f1; }

        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1 id="titulo-periodo">Panorama Contábil</h1>
            <p>Resumo Executivo de Resultados</p>
        </div>
        <div class="header-right">
            Gerado em: <span id="data-geracao"></span>
        </div>
    </div>

    <div class="grid" id="cards-container"></div>

    <div class="footer">
        Sistema SGPC - Dashboard Executivo
    </div>

    <script>
        function formatarMilhoes(valor) {
            if (valor === undefined || valor === null) return "R$ 0,0 mi";
            const num = Number(valor) / 1000000;
            return (num < 0 ? "-R$ " : "R$ ") + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }

        function criarCard(titulo, valor, tipo) {
            return `
                <div class="card ${tipo}">
                    <div class="card-title">${titulo}</div>
                    <div class="card-value">${formatarMilhoes(valor)}</div>
                </div>
            `;
        }

        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            document.getElementById("data-geracao").innerText = new Date().toLocaleDateString('pt-BR');

            if (!historicoId) return;

            try {
                const res = await fetch(`/historico_panorama/${historicoId}`);
                const data = await res.json();
                const d = data.dados;
                
                document.getElementById("titulo-periodo").innerText = "Panorama - " + (data.periodo || "Período");

                let html = "";
                html += criarCard("Caixa e Equivalente de Caixa (BP)", d.caixa_bp, "neutral");
                html += criarCard("Ativo Total", d.ativo_total, "neutral");
                html += criarCard("Passivo Total", d.passivo_total, "neutral");
                html += criarCard("Patrimônio Líquido", d.patrimonio_liquido, "neutral");
                html += criarCard("Receitas Realizadas", d.receita_realizada, "positive");
                html += criarCard("Despesas Empenhadas", d.despesa_empenhada, "negative");
                
                const orc = d.superavit_orcamentario || 0;
                html += criarCard(orc < 0 ? "Déficit Orçamentário" : "Superávit Orçamentário", orc, orc < 0 ? "negative" : "positive");
                
                const pat = d.superavit_patrimonial || 0;
                html += criarCard(pat < 0 ? "Déficit Patrimonial" : "Superávit Patrimonial", pat, pat < 0 ? "negative" : "positive");
                
                const fin = d.superavit_financeiro || 0;
                html += criarCard(fin < 0 ? "Déficit Financeiro" : "Superávit Financeiro", fin, fin < 0 ? "negative" : "positive");

                document.getElementById("cards-container").innerHTML = html;
            } catch (e) {
                document.getElementById("cards-container").innerHTML = "<p>Erro ao carregar os dados.</p>";
            }
        });
    </script>
</body>
</html>"""

with open(r"pc_frontend\relatorio_panorama.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("[OK] Novo visual do PDF criado (Design Premium)!")

# ==========================================
# 2. MATAR AS DUAS ABAS NO FRONTEND
# ==========================================
front_path = r"pc_frontend\panorama.html"
shutil.copy2(front_path, f"{front_path}.bak_fixduasabas_{ts}")
c = open(front_path, encoding='utf-8').read()

# Remove qualquer resquício de onclick="gerarPDF()" do HTML
c = re.sub(r'onclick="gerarPDF\(\)"', '', c)

# Remove scripts antigos que possam ter ficado
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const botoes = Array\.from.*?</script>', '', c, flags=re.DOTALL)

# Adiciona o script final, à prova de duplo clique
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Encontra o botão de PDF baseado no texto
            const botoes = Array.from(document.querySelectorAll('button, a, div'));
            const btnPdf = botoes.find(b => b.innerText.trim().toUpperCase().includes('GERAR PDF'));
            
            if (btnPdf) {
                // Clona o botão para remover QUALQUER event listener antigo acoplado a ele
                const novoBtn = btnPdf.cloneNode(true);
                btnPdf.parentNode.replaceChild(novoBtn, btnPdf);
                
                // Adiciona apenas o nosso clique
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
print("[OK] Botão PDF blindado contra duplo clique (removeu onclick antigo)!")

# ==========================================
# 3. GARANTIR ROTA CORRETA NO MAIN.PY
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fixduasabas_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

if 'http://127.0.0.1:9994/relatorio_panorama?historico_id=' not in c_back:
    c_back = c_back.replace(
        'http://127.0.0.1:9994/panorama?historico_id={historico_id}',
        'http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}'
    )
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Rota do Playwright forçada para o novo relatório!")
else:
    print("[OK] Rota do Playwright já estava correta.")

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
