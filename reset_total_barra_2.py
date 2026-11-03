import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_barra_def_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Encontra a div da barra de botões e substitui o conteúdo inteiro
padrao = r'<div class="top-bar">.*?</div>'
nova_barra = '''<div class="top-bar">
        <a href="/" class="btn" style="background:#ed8936; text-decoration:none; display:inline-block; padding:8px 15px; border-radius:6px; font-weight:bold; color:#fff; font-size:14px;">← Voltar</a>
        <button class="btn" style="background:#38a169;" onclick="if(typeof exibirSelecionado === 'function') exibirSelecionado()">Exibir Selecionado</button>
        <button class="btn" style="background:#e53e3e;" onclick="if(typeof excluirSelecionado === 'function') excluirSelecionado()">Excluir Selecionado</button>
        <button class="btn btn-pdf" onclick="gerarPDFPanorama()">Gerar PDF</button>
        <button class="btn" style="background:#38a169;" onclick="if(typeof salvarPanorama === 'function') salvarPanorama()">Confirmar e Salvar</button>
    </div>'''

if re.search(padrao, c, flags=re.DOTALL):
    c = re.sub(padrao, nova_barra, c, flags=re.DOTALL)
    print("[OK] Barra de botões totalmente substituída (Voltar é um link puro)!")
else:
    print("[AVISO] Div top-bar não encontrada. Tentando substituir botão por botão...")
    # Fallback: substitui qualquer tag que tenha a palavra Voltar por um link puro
    c = re.sub(r'<(?:button|a)[^>]*>[^<]*Voltar[^<]*</(?:button|a)>', '<a href="/" class="btn" style="background:#ed8936; text-decoration:none; display:inline-block; padding:8px 15px; border-radius:6px; font-weight:bold; color:#fff; font-size:14px;">← Voltar</a>', c, flags=re.IGNORECASE)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Processo finalizado!")
