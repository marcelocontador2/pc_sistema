import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. FRONTEND: Obrigar seleção de histórico no botão de Despesas
# ==========================================
front_path = r"pc_frontend\analise_comparativo_despesas.html"
shutil.copy2(front_path, f"{front_path}.bak_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# Substitui a chamada antiga do botão
c_front = c_front.replace('onclick="window.print()"', 'onclick="gerarPDF()"')

# Injeta a função gerarPDF no final do script
funcao_pdf = """
        function gerarPDF() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            window.open(`/gerar_pdf_comparativo_despesas?historico_id=${sel.value}`, '_blank');
        }
        
        document.addEventListener('DOMContentLoaded', () => {"""
        
if "function gerarPDF()" not in c_front:
    c_front = c_front.replace("        document.addEventListener('DOMContentLoaded', () => {", funcao_pdf)

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Frontend de Despesas atualizado (botão exige histórico).")

# ==========================================
# 2. BACKEND: Aceitar historico_id na rota de Despesas
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Altera a assinatura da rota
c_back = c_back.replace(
    'def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3"):',
    'def gerar_pdf_comparativo_despesas(periodo_atual: str = None, historico_id: int = None):'
)

# Altera a URL do Playwright
url_antiga = 'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'
url_nova = '''if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'''

c_back = c_back.replace(url_antiga, url_nova)
open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Backend de Despesas atualizado (Playwright aceita historico_id).")

# ==========================================
# 3. RELATÓRIO: Ler os dados do histórico
# ==========================================
relatorio_path = r"pc_frontend\relatorio_comparativo_despesas_v2.html"
if not os.path.exists(relatorio_path):
    # Tenta achar variações do nome
    for f in os.listdir("pc_frontend"):
        if "relatorio_comparativo_despesas" in f:
            relatorio_path = os.path.join("pc_frontend", f)
            break

if os.path.exists(relatorio_path):
    shutil.copy2(relatorio_path, f"{relatorio_path}.bak_{ts}")
    c_rel = open(relatorio_path, encoding='utf-8').read()

    # Script que busca os dados da API correta
    script_injecao = """
        const urlParams = new URLSearchParams(window.location.search);
        const historicoId = urlParams.get('historico_id');
        const periodoAtual = urlParams.get('periodo_atual');
        
        let urlFetch = '';
        if (historicoId) {
            urlFetch = `/historico_comparativo_despesas/${historicoId}`;
        } else {
            urlFetch = `/api/comparativo_despesas_v2/${periodoAtual}`;
        }
        
        fetch(urlFetch + '?_t=' + Date.now())
            .then(res => res.json())
            .then(data => {
                const dadosReais = data.dados ? data.dados : data;
    """

    # Troca o fetch antigo (seja qual for) pelo novo
    padrao_fetch = r'fetch\([^\)]*comparativo_despesas[^\)]*\)\s*\.then\(res => res\.json\(\)\)\s*\.then\(data => \{'
    
    if re.search(padrao_fetch, c_rel):
        c_rel = re.sub(padrao_fetch, script_injecao, c_rel)
        open(relatorio_path, 'w', encoding='utf-8').write(c_rel)
        print(f"[OK] Relatório ({os.path.basename(relatorio_path)}) atualizado para ler histórico.")
    else:
        print("[AVISO] Fetch do relatório de despesas não encontrado no formato exato. Pode precisar de ajuste manual.")

else:
    print("[ERRO] Arquivo HTML do relatório de despesas não encontrado.")

