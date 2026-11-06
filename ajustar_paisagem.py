import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_paisagem_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza o bloco da rota do PDF consolidado
idx_rota = codigo.find("def gerar_pdf_relatorio_consolidado")
if idx_rota == -1:
    print("[ERRO] Rota do PDF consolidado não encontrada.")
    exit()

fim_rota = codigo.find("\n@app.", idx_rota)
if fim_rota == -1:
    fim_rota = codigo.find("\ndef ", idx_rota + 10)
if fim_rota == -1:
    fim_rota = idx_rota + 8000

bloco_rota = codigo[idx_rota:fim_rota]

# =========================================================
# 1. Alterar a CAPA: remover "Executiva" e ajustar para paisagem
# =========================================================
# Encontra o HTML da capa dentro da rota
padrao_capa = re.compile(
    r'(<div class="capa">.*?</div>\s*</body>)',
    re.DOTALL
)

# Substitui "Análise Contábil Executiva" por "Análise Contábil"
bloco_rota = bloco_rota.replace('Análise Contábil Executiva', 'Análise Contábil')
bloco_rota = bloco_rota.replace('Análise Contábil Executiva', 'Análise Contábil')

# Ajusta o CSS da capa para paisagem (A4: 297 x 210)
bloco_rota = bloco_rota.replace(
    '.capa {{ width: 210mm; height: 297mm;',
    '.capa {{ width: 297mm; height: 210mm;'
)
# Ajusta a faixa azul para ocupar a largura maior
bloco_rota = bloco_rota.replace('width: 100%; padding: 60px 0; margin-bottom: 60px;',
                                'width: 100%; padding: 40px 0; margin-bottom: 30px;')
# Ajusta o tamanho do título para não ficar gigante em paisagem
bloco_rota = bloco_rota.replace('font-size: 34px;', 'font-size: 28px;')
bloco_rota = bloco_rota.replace('font-size: 16px;', 'font-size: 14px;')

# =========================================================
# 2. Alterar o Playwright para gerar PDF em paisagem
# =========================================================
# Procura o page.pdf da capa
bloco_rota = bloco_rota.replace(
    'capa_bytes = page.pdf(format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})',
    'capa_bytes = page.pdf(format="A4", orientation="landscape", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})'
)

# =========================================================
# 3. Alterar a normalização para PAISAGEM
# =========================================================
# Encontra a função normalizar_pagina
padrao_norm = re.compile(
    r'(def normalizar_pagina\(page_obj\):.*?)(?=\n\s*#|\n\s*def |\n\s*db_path|\Z)',
    re.DOTALL
)

match_norm = padrao_norm.search(bloco_rota)
if match_norm:
    bloco_norm_antigo = match_norm.group(1)
    
    bloco_norm_novo = '''def normalizar_pagina(page_obj):
        """Garante que a página esteja em A4 PAISAGEM, escalonando se necessário."""
        try:
            A4_W, A4_H = 842, 595  # A4 paisagem em pontos
            
            w = float(page_obj.mediabox.width)
            h = float(page_obj.mediabox.height)
            if w == 0 or h == 0:
                return page_obj

            # Detecta se está em RETRATO (h > w) e rotaciona para paisagem
            if h > w:
                page_obj.rotate(-90)
                w, h = h, w

            # Calcula escala para caber em A4 paisagem mantendo proporção
            scale_w = A4_W / w
            scale_h = A4_H / h
            scale = min(scale_w, scale_h)

            if abs(scale - 1.0) > 0.01:
                page_obj.add_transformation(Transformation().scale(scale))
                new_w = w * scale
                new_h = h * scale
                offset_x = (A4_W - new_w) / 2
                offset_y = (A4_H - new_h) / 2
                page_obj.add_transformation(Transformation().translate(offset_x, offset_y))

            # Define o mediabox para A4 paisagem
            page_obj.mediabox.upper_right = (A4_W, A4_H)
            page_obj.mediabox.lower_left = (0, 0)
            return page_obj
        except Exception as e:
            print(f"[AVISO] Falha ao normalizar página: {e}")
            return page_obj
    
    '''
    
    bloco_rota = bloco_rota.replace(bloco_norm_antigo, bloco_norm_novo)
    print("[OK] Função normalizar_pagina ajustada para paisagem.")
else:
    print("[AVISO] Função normalizar_pagina não encontrada.")

# =========================================================
# 4. Alterar o page.pdf dos módulos para paisagem (caso exista)
# =========================================================
bloco_rota = bloco_rota.replace(
    'format="A4", print_background=True,\n                                     margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"}',
    'format="A4", orientation="landscape", print_background=True,\n                                     margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"}'
)

# =========================================================
# Substitui o bloco no código
# =========================================================
codigo = codigo.replace(bloco_rota, bloco_rota)

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo com capa em paisagem e 'Executiva' removido.")
