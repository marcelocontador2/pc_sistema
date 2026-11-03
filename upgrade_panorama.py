import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CRIAR O NOVO RELATÓRIO MODERNO (HTML)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        @page { size: A4 landscape; margin: 0; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f4f7f6;
            margin: 0;
            padding: 40px;
            color: #2d3748;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
            color: #1a202c;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .header .subtitle {
            font-size: 16px;
            color: #718096;
            font-weight: 600;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .card {
            background: #ffffff;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border-left: 6px solid #3182ce;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .card.positive { border-left-color: #38a169; }
        .card.negative { border-left-color: #e53e3e; }

        .card-title {
            font-size: 13px;
            font-weight: 600;
            color: #718096;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: #2d3748;
        }

        .card.positive .card-value { color: #2f855a; }
        .card.negative .card-value { color: #c53030; }

        .footer {
            position: fixed;
            bottom: 20px;
            left: 40px;
            right: 40px;
            text-align: center;
            font-size: 11px;
            color: #a0aec0;
            border-top: 1px solid #e2e8f0;
            padding-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="subtitle">Painel de Resultados Gerais</div>
            <h1 id="titulo-periodo">Panorama Contábil</h1>
        </div>
        <div class="subtitle" id="data-geracao"></div>
    </div>

    <div class="grid" id="cards-container">
        <!-- Os cards serão injetados via JavaScript -->
    </div>

    <div class="footer">
        Sistema SGPC - Gerado em <span id="footer-data"></span>
    </div>

    <script>
        function formatarMilhoes(valor) {
            if (valor === undefined || valor === null) return "R$ 0,0 mi";
            const num = Number(valor) / 1000000;
            return (num < 0 ? "-R$ " : "R$ ") + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }

        function criarCard(titulo, valor, tipo) {
            let classe = "";
            if (tipo === 'positivo') classe = "positive";
            if (tipo === 'negativo') classe = "negative";
            
            return `
                <div class="card ${classe}">
                    <div class="card-title">${titulo}</div>
                    <div class="card-value">${formatarMilhoes(valor)}</div>
                </div>
            `;
        }

        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            const dataAtual = new Date().toLocaleDateString('pt-BR');
            document.getElementById("data-geracao").innerText = "Gerado em: " + dataAtual;
            document.getElementById("footer-data").innerText = dataAtual;

            if (!historicoId) return;

            try {
                // Busca os dados do histórico no backend
                const res = await fetch(`/historico_panorama/${historicoId}`);
                const data = await res.json();
                const d = data.dados; // Objeto com os valores

                document.getElementById("titulo-periodo").innerText = "Panorama - " + (data.periodo || "Período");

                // Monta os cards com base nos dados do JSON
                let html = "";
                html += criarCard("Caixa e Equivalente de Caixa (BP)", d.caixa_bp, "neutro");
                html += criarCard("Ativo Total", d.ativo_total, "neutro");
                html += criarCard("Passivo Total", d.passivo_total, "neutro");
                html += criarCard("Patrimônio Líquido", d.patrimonio_liquido, "neutro");
                html += criarCard("Receitas Realizadas (BO)", d.receita_realizada, "positivo");
                html += criarCard("Despesas Empenhadas (BO)", d.despesa_empenhada, "negativo");
                
                const orc = d.superavit_orcamentario || 0;
                html += criarCard(orc < 0 ? "Déficit Orçamentário" : "Superávit Orçamentário", orc, orc < 0 ? "negativo" : "positivo");
                
                const pat = d.superavit_patrimonial || 0;
                html += criarCard(pat < 0 ? "Déficit Patrimonial (DVP)" : "Superávit Patrimonial (DVP)", pat, pat < 0 ? "negativo" : "positivo");
                
                const fin = d.superavit_financeiro || 0;
                html += criarCard(fin < 0 ? "Déficit Financeiro (BP)" : "Superávit Financeiro (BP)", fin, fin < 0 ? "negativo" : "positivo");

                document.getElementById("cards-container").innerHTML = html;

            } catch (e) {
                console.error("Erro ao carregar dados:", e);
                document.getElementById("cards-container").innerHTML = "<p style='color:red;'>Erro ao carregar os dados do histórico.</p>";
            }
        });
    </script>
</body>
</html>"""

with open("pc_frontend/relatorio_panorama.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("[OK] Novo arquivo 'relatorio_panorama.html' criado (Layout Moderno)!")

# ==========================================
# 2. ATUALIZAR O BACKEND E O FRONTEND
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_moderno_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# A. Atualiza a rota do Playwright para apontar para o novo HTML
c_back = c_back.replace(
    'http://127.0.0.1:9994/panorama?historico_id={historico_id}',
    'http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}'
)
print("[OK] Rota do Playwright atualizada para o novo relatório!")

# B. Cria a rota do FastAPI para servir o novo HTML (se não existir)
if '@app.get("/relatorio_panorama")' not in c_back:
    rota_html = '''
@app.get("/relatorio_panorama")
def serve_relatorio_panorama():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "relatorio_panorama.html")
    return FileResponse(caminho)
'''
    c_back += rota_html
    print("[OK] Rota /relatorio_panorama adicionada ao Backend!")

open(back_path, 'w', encoding='utf-8').write(c_back)

# C. Corrigir o duplo clique/dupla aba no panorama.html
front_path = r"pc_frontend\panorama.html"
shutil.copy2(front_path, f"{front_path}.bak_moderno_{ts}")
c_front = open(front_path, encoding='utf-8').read()

inicio_func = c_front.find('function gerarPDF()')
if inicio_func != -1:
    idx_chave = c_front.find('{', inicio_func)
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c_front):
        if c_front[i] == '{': nivel += 1
        elif c_front[i] == '}': nivel -= 1
        i += 1
    
    nova_func = """let isGeneratingPDF = false;
        function gerarPDF() {
            if (isGeneratingPDF) return; // Evita dupla execução
            isGeneratingPDF = true;
            setTimeout(() => isGeneratingPDF = false, 2000); // Destrava após 2 segundos

            const check = document.querySelector(".check-historico:checked");
            if (!check) { 
                alert("Atenção: Marque um relatório no histórico antes de gerar o PDF."); 
                return; 
            }
            
            const url = `/gerar_pdf_panorama/${check.value}`;
            window.open(url, '_blank');
        }"""
    c_front = c_front[:inicio_func] + nova_func + c_front[i:]
    print("[OK] Botão PDF da tela Panorama protegido contra duplo clique (duas abas)!")

open(front_path, 'w', encoding='utf-8').write(c_front)

# Validar sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
