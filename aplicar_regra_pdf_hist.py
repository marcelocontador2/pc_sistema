import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. ATUALIZAR O FRONTEND (Enviar historico_id)
# ==========================================
front_path = r"pc_frontend\analise_comparativo_receitas.html"
shutil.copy2(front_path, f"{front_path}.bak_{ts}")
c_front = open(front_path, encoding='utf-8').read()

antigo_btn = "window.open(`/gerar_pdf_comparativo_receitas?periodo_atual=${periodo}`, '_blank');"
novo_btn = "window.open(`/gerar_pdf_comparativo_receitas?historico_id=${sel.value}`, '_blank');"

if antigo_btn in c_front:
    c_front = c_front.replace(antigo_btn, novo_btn)
    open(front_path, 'w', encoding='utf-8').write(c_front)
    print("[OK] Frontend atualizado para enviar o ID do Histórico!")
else:
    print("[AVISO] Botão do frontend não encontrado ou já atualizado.")

# ==========================================
# 2. ATUALIZAR O BACKEND (Receber historico_id)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Altera a assinatura da rota para aceitar historico_id
assinatura_antiga = 'def gerar_pdf_comparativo_receitas(periodo_atual: str):'
assinatura_nova = 'def gerar_pdf_comparativo_receitas(periodo_atual: str = None, historico_id: int = None):'
if assinatura_antiga in c_back:
    c_back = c_back.replace(assinatura_antiga, assinatura_nova)

# Altera a URL que o Playwright vai abrir
url_antiga = 'url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'
url_nova = '''if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'''

if url_antiga in c_back:
    c_back = c_back.replace(url_antiga, url_nova)
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Backend atualizado para repassar o historico_id para o Playwright!")
else:
    print("[AVISO] URL do Playwright não encontrada no main.py. Pode estar em outro formato.")

# ==========================================
# 3. ACHAR E ATUALIZAR A PÁGINA DO RELATÓRIO
# ==========================================
front_dir = r"pc_frontend"
arquivo_relatorio = None
for f in os.listdir(front_dir):
    if "relatorio_comparativo_receitas" in f and f.endswith(".html"):
        arquivo_relatorio = os.path.join(front_dir, f)
        break

if arquivo_relatorio:
    print(f"\n[INFO] Arquivo de relatório encontrado: {arquivo_relatorio}")
    shutil.copy2(arquivo_relatorio, f"{arquivo_relatorio}.bak_{ts}")
    c_rel = open(arquivo_relatorio, encoding='utf-8').read()
    
    # Procura onde ele busca os dados (fetch) e injeta a lógica do historico_id
    padrao_fetch = r"fetch\([`'\"]\/api\/comparativo_receitas_v2.*?\)"
    
    script_injecao = """
        // INJEÇÃO DE DADOS DO HISTÓRICO
        const urlParams = new URLSearchParams(window.location.search);
        const historicoId = urlParams.get('historico_id');
        
        let urlFetch = '';
        if (historicoId) {
            urlFetch = `/historico_comparativo_receitas/${historicoId}`;
        } else {
            const periodo = urlParams.get('periodo_atual');
            urlFetch = `/api/comparativo_receitas_v2/${periodo}`;
        }
        
        fetch(urlFetch + '?_t=' + Date.now())
            .then(res => res.json())
            .then(data => {
                // Se for do histórico, os dados vêm dentro de 'data.dados', senão é 'data' direto
                const dadosReais = data.dados ? data.dados : data;
                // AQUI ELE CHAMA A FUNÇÃO QUE JÁ EXISTE NA SUA PÁGINA PARA RENDERIZAR
                if (typeof renderizarRelatorio === 'function') {
                    renderizarRelatorio(dadosReais);
                } else {
                    console.log("Aviso: função de renderizar não encontrada. Dados:", dadosReais);
                }
            });
    """
    print("[OK] Lógica de injeção preparada. (Verifique o arquivo gerado)")
    
    # Como não sei o nome exato da função de renderização do seu relatório, vou salvar um arquivo txt de instruções para você
    with open("instrucoes_relatorio.txt", "w", encoding="utf-8") as f:
        f.write("Vá no arquivo " + arquivo_relatorio + " e altere o fetch para buscar do histórico.\n")
        f.write("Use este código como base:\n\n" + script_injecao)
    print("[AVISO] O arquivo do relatório precisa de um ajuste manual no JS. Abri instruções em 'instrucoes_relatorio.txt'.")
else:
    print("\n[ERRO] Não encontrei o arquivo HTML do relatório de receitas na pasta pc_frontend.")

