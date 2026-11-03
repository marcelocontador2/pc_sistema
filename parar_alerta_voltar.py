import shutil, datetime, re

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_stop_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Altera o botão "Voltar" para blindar o evento contra propagação
# Isso garante que ele execute APENAS o window.location e ignore outros eventos
novo_btn_voltar = """<button class="btn" style="background:#ed8936;" onclick="event.stopPropagation(); event.preventDefault(); window.location.href='/'; return false;">← Voltar</button>"""

# Substitui a tag do botão antigo por esse novo
c = re.sub(r'<button[^>]*onclick="[^"]*window\.location[^"]*"[^>]*>.*?Voltar.*?</button>', novo_btn_voltar, c, flags=re.DOTALL | re.IGNORECASE)
c = re.sub(r'<a[^>]*>.*?Voltar.*?</a>', novo_btn_voltar, c, flags=re.DOTALL | re.IGNORECASE)

# 2. Remove qualquer script global antigo de clique que possa estar no body
c = re.sub(r'<script>\s*document\.addEventListener\(\'click\', function.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*window\.addEventListener\(\'click\', function.*?</script>', '', c, flags=re.DOTALL)

# 3. Adiciona um CSS global para garantir que o botão volte a ter o visual de botão (ele pode ter virado um link)
c = c.replace('</style>', """
        .btn {
            display: inline-block;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            color: white;
        }
    </style>""")

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Voltar' blindado com stopPropagation e visual corrigido!")
