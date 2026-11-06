import re, os

arquivos = [
    r"pc_frontend\relatorio_comparativo_receitas_v2.html",
    r"pc_frontend\relatorio_comparativo_despesas_v2.html"
]

for arq in arquivos:
    if not os.path.exists(arq):
        print(f"[AVISO] Arquivo não encontrado: {arq}")
        continue
        
    print(f"\n{'='*50}\nAnalisando: {arq}")
    with open(arq, "r", encoding="utf-8") as f:
        html = f.read()

    # Procura a função de exclusão
    match = re.search(r'async function excluirSelecionado\(\)\s*\{.*?\n\s*\}', html, re.DOTALL)
    if match:
        print("--- CÓDIGO ATUAL DA FUNÇÃO EXCLUIR ---")
        print(match.group(0))
    else:
        print("[ERRO] Função 'excluirSelecionado' não encontrada.")
        
    # Verifica se há botão de excluir no HTML
    if "onclick=\"excluirSelecionado()\"" in html or "id=\"btn-excluir\"" in html:
        print("[OK] Botão de excluir encontrado no HTML.")
    else:
        print("[AVISO] Botão de excluir não encontrado no HTML (verifique os IDs).")
        
    # Verifica se a rota de exclusão múltipla já existe no backend (só para referência)
    if "excluir_multiplos" in html:
        print("[INFO] A tela já tenta usar exclusão múltipla.")
    else:
        print("[INFO] A tela usa exclusão simples (1 por vez).")
