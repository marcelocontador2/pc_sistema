import shutil
import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_toast_verde")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona o CSS do toast (se ainda não existir)
if ".toast-producao" not in html:
    css_toast = '''
    <style>
        .toast-producao {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #28a745;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif;
            font-size: 14px;
            font-weight: bold;
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideIn 0.3s ease-out;
        }
        .toast-producao .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            animation: spin 1s linear infinite;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    '''
    # Insere o CSS antes do </head>
    html = html.replace("</head>", css_toast + "</head>")
    print("✅ CSS do toast adicionado.")

# 2. Substitui a função gerarPDF para mostrar o toast
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
        
        // Remove toast anterior, se existir
        const toastAntigo = document.getElementById('toast-producao');
        if (toastAntigo) toastAntigo.remove();
        
        // Cria o toast verde
        const toast = document.createElement('div');
        toast.id = 'toast-producao';
        toast.className = 'toast-producao';
        toast.innerHTML = '<div class="spinner"></div> Relatório em Produção...';
        document.body.appendChild(toast);
        
        // Cria um link temporário para forçar o download
        const link = document.createElement('a');
        link.href = url;
        link.download = 'relatorio_consolidado_' + id + '.pdf';
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        
        // Remove o link e o toast após um tempo
        setTimeout(() => {
            document.body.removeChild(link);
            if (toast) toast.remove();
        }, 6000);
    }'''
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    print("✅ Função 'gerarPDF' atualizada para mostrar o toast verde.")
else:
    print("❌ Função 'gerarPDF' não encontrada.")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML atualizado!")
