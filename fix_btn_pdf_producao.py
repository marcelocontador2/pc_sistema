import shutil
import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_btn_pdf_producao")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Localiza a função gerarPDF atual
idx_inicio = html.find("function gerarPDF()")
if idx_inicio == -1:
    idx_inicio = html.find("async function gerarPDF()")

if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    nova_funcao = '''function gerarPDF() {
        const checkbox = document.querySelector('#lista-historico input[type="checkbox"]:checked');
        if (!checkbox) { alert("Selecione um histórico na lista lateral."); return; }
        
        const id = checkbox.value;
        const url = '/gerar_pdf_relatorio_consolidado/' + id;
        
        // Encontra o botão que disparou a ação
        const btn = document.querySelector('button[onclick="gerarPDF()"]');
        const textoOriginal = btn ? btn.innerText : 'Gerar PDF';
        
        // Mostra mensagem "Relatório em Produção"
        if (btn) {
            btn.innerText = 'Relatório em Produção...';
            btn.disabled = true;
            btn.style.opacity = '0.7';
            btn.style.cursor = 'wait';
        }
        
        // Cria um link temporário para forçar o download
        const link = document.createElement('a');
        link.href = url;
        link.download = 'relatorio_consolidado_' + id + '.pdf';
        link.target = '_blank';
        document.body.appendChild(link);
        
        // Simula o clique e aguarda um tempo para o navegador processar
        link.click();
        
        // Remove o link após um tempo
        setTimeout(() => {
            document.body.removeChild(link);
            
            // Restaura o botão após 5 segundos (tempo estimado para o PDF ser gerado)
            setTimeout(() => {
                if (btn) {
                    btn.innerText = textoOriginal;
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.style.cursor = 'pointer';
                }
            }, 5000);
        }, 500);
    }'''
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    print("✅ Função 'gerarPDF' atualizada para mostrar 'Relatório em Produção...' enquanto gera.")
else:
    print("❌ Função 'gerarPDF' não encontrada.")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML atualizado!")
