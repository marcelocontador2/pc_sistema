import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_injecao_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Verifica se o core do JS (carregarPanorama) ainda está vivo
if "function carregarPanorama" not in c:
    print("[AVISO] A função carregarPanorama sumiu! O JS pode ter sido apagado.")
else:
    print("[OK] A função principal carregarPanorama está intacta.")

# 2. Corrige o botão Voltar para ser totalmente independente
# Adicionamos type="button" para não submeter form, e um "return false" para parar o evento
novo_btn_voltar = """<button type="button" class="btn" style="background:#ed8936;" onclick="event.stopPropagation(); event.preventDefault(); window.location.href='/'; return false;">← Voltar</button>"""

# Substitui a tag atual
c = re.sub(r'<button[^>]*>.*?←.*?Voltar.*?</button>', novo_btn_voltar, c, flags=re.IGNORECASE | re.DOTALL)
c = re.sub(r'<button[^>]*>.*?Voltar.*?</button>', novo_btn_voltar, c, flags=re.IGNORECASE | re.DOTALL)
c = re.sub(r'<a[^>]*>.*?Voltar.*?</a>', novo_btn_voltar, c, flags=re.IGNORECASE | re.DOTALL)

# 3. Conserta os outros botões para não recarregarem a página acidentalmente
c = c.replace('<button class="btn" style="background:#38a169;" onclick="if(typeof exibirSelecionado', '<button type="button" class="btn" style="background:#38a169;" onclick="if(typeof exibirSelecionado')
c = c.replace('<button class="btn" style="background:#e53e3e;" onclick="if(typeof excluirSelecionado', '<button type="button" class="btn" style="background:#e53e3e;" onclick="if(typeof excluirSelecionado')
c = c.replace('<button class="btn btn-pdf" onclick="gerarPDFPanorama()"', '<button type="button" class="btn btn-pdf" onclick="gerarPDFPanorama()"')
c = c.replace('<button class="btn" style="background:#38a169;" onclick="if(typeof salvarPanorama', '<button type="button" class="btn" style="background:#38a169;" onclick="if(typeof salvarPanorama')

# 4. Garante que nenhum script antigo esteja bloqueando o botão
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*// Seleciona.*?</script>', '', c, flags=re.DOTALL)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão Voltar substituído por versão puramente HTML!")
