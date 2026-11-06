import shutil, datetime, re

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_undo_fontes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Reverter a troca de "ArialUnicode" de volta para "Helvetica" nas linhas do DFC
#    (para restaurar a funcionalidade do DFC)
codigo = codigo.replace('set_font("ArialUnicode"', 'set_font("Helvetica"')
# Reverter a injeção de add_font(ArialUnicode) nas funções
codigo = re.sub(
    r'\s*pdf\.add_font\("ArialUnicode", "", r"C:/Windows/Fonts/arial\.ttf", uni=True\)\s*pdf\.add_font\("ArialUnicode", "B", r"C:/Windows/Fonts/arial\.ttf", uni=True\)\s*pdf\.add_font\("ArialUnicode", "I", r"C:/Windows/Fonts/arial\.ttf", uni=True\)\s*',
    '\n',
    codigo
)
# Reverter fonte_padrao do BF (linha 1712)
codigo = codigo.replace('fonte_padrao = "ArialUnicode"', 'fonte_padrao = "Helvetica"')

# 2. Substituir o monkey-patch antigo por uma versão mais robusta
#    que faz o override de `set_font` para trocar "Helvetica" por "ArialUTF8"
padrao_mp = re.compile(
    r'# ===== MONKEY-PATCH PARA UTF-8 NO FPDF =====.*?# ===== FIM DO MONKEY-PATCH =====',
    re.DOTALL
)

novo_mp = f'''# ===== MONKEY-PATCH PARA UTF-8 NO FPDF (v2) =====
import os as _os_mp
_FONT_PATH_UTF8 = "C:/Windows/Fonts/arial.ttf"

if _os_mp.path.exists(_FONT_PATH_UTF8):
    try:
        from fpdf import FPDF as _FPDF_Original
        import fpdf as _fpdf_module

        _original_set_font = _FPDF_Original.set_font

        def _set_font_utf8(self, family="helvetica", style="", size=0):
            # Se for "Helvetica", substitui por "ArialUTF8"
            if str(family).lower() in ("helvetica", "arial"):
                try:
                    if "ArialUTF8" not in self.fonts:
                        self.add_font("ArialUTF8", "", _FONT_PATH_UTF8, uni=True)
                        self.add_font("ArialUTF8", "B", _FONT_PATH_UTF8, uni=True)
                        self.add_font("ArialUTF8", "I", _FONT_PATH_UTF8, uni=True)
                    family = "ArialUTF8"
                except Exception:
                    pass
            return _original_set_font(self, family, style, size)

        _FPDF_Original.set_font = _set_font_utf8
    except Exception as _e:
        print(f"[FPDF-UTF8] Erro no monkey-patch: {{_e}}")
# ===== FIM DO MONKEY-PATCH =====
'''

if padrao_mp.search(codigo):
    codigo = padrao_mp.sub(novo_mp, codigo)
    print("[OK] Monkey-patch antigo removido e substituído pela v2.")
else:
    print("[AVISO] Monkey-patch antigo não encontrado. Inserindo no início do app.")
    # Se não existir, insere após app = FastAPI(
    padrao_app = re.compile(r'(app\s*=\s*FastAPI\s*\([^)]*\))')
    codigo = padrao_app.sub(r'\1\n\n' + novo_mp, codigo, count=1)

# 3. Valida sintaxe
try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py corrigido com sucesso.")
print("[INFO] O monkey-patch v2 intercepta set_font() e troca Helvetica por ArialUTF8 automaticamente.")
