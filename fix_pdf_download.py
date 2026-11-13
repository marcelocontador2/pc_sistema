import shutil

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_pdf_download")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a função gerarPDF para forçar o download do arquivo
nova_funcao = '''function gerarPDF() {
    const checkbox = document.querySelector('#lista-historico input[type="checkbox"]:checked');
    if (!checkbox) { alert("Selecione um histórico na lista lateral."); return; }
    
    const id = checkbox.value;
    const url = '/gerar_pdf_relatorio_consolidado/' + id;
    
    // Cria um link temporário para forçar o download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'relatorio_consolidado_' + id + '.pdf';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}'''

# Localiza a função gerarPDF atual e substitui
idx_inicio = html.find("function gerarPDF()")
if idx_inicio == -1:
    print("⚠️ Função 'gerarPDF' não encontrada. Tentando abordagem alternativa...")
else:
    i = html.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    print("✅ Função 'gerarPDF' atualizada para forçar download.")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ HTML salvo! Reinicie o servidor e teste o botão 'Gerar PDF'.")
