import shutil, datetime

arquivo = 'analise_comparativo_receitas.html'
shutil.copy2(arquivo, f"{arquivo}.bak_pdf_safe_{datetime.datetime.now().strftime('%H%M%S')}")
c = open(arquivo, encoding='utf-8').read()

inicio = c.find('function gerarPDF() {')
if inicio != -1:
    # Encontra a chave de abertura e conta até fechar a função
    idx_chave = c.find('{', inicio)
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c):
        if c[i] == '{': nivel += 1
        elif c[i] == '}': nivel -= 1
        i += 1
    
    # Nova função blindada (sem regex JS complexo)
    nova_funcao = """function gerarPDF() {
            const sel = document.querySelector('input[name="historico"]:checked');
            let periodo = "";
            
            // Tenta pegar o período do Histórico selecionado
            if (sel) {
                const span = sel.nextElementSibling;
                if (span) {
                    const texto = span.innerText;
                    const partes = texto.split('|');
                    if (partes.length > 0) {
                        periodo = partes[0].replace('Período:', '').trim();
                    }
                }
            }
            
            // Se não achou no histórico, pega dos filtros do topo
            if (!periodo) {
                const ano = document.getElementById('ano').value;
                const tipo = document.getElementById('tipo').value;
                const valor = document.getElementById('valor').value;
                periodo = `${ano}-${tipo}-${valor}`;
            }
            
            // Chama a rota
            window.open(`/gerar_pdf_comparativo_receitas?periodo_atual=${periodo}`, '_blank');
        }"""
    
    c = c[:inicio] + nova_funcao + c[i:]
    open(arquivo, 'w', encoding='utf-8').write(c)
    print("[OK] Função 'gerarPDF()' substituída com sucesso e regra de negócio aplicada!")
else:
    print("[ERRO] Função gerarPDF não encontrada no arquivo.")
