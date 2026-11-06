import glob, os, shutil, re

# 1. Restaura o main.py do backup mais recente ANTES da quebra
backups = glob.glob(r"pc_backend\main_backup_undo_fontes_*.py")
if not backups:
    print("[ERRO] Backup não encontrado.")
    exit()

backup = max(backups, key=os.path.getctime)
print(f"[OK] Restaurando de: {backup}")
shutil.copy2(backup, r"pc_backend\main.py")

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe original válida.")
except SyntaxError as e:
    print(f"[ERRO] Backup ainda quebrado na linha {e.lineno}: {e.msg}")
    exit()

# 2. Remove qualquer monkey-patch antigo
padrao_mp = re.compile(
    r'# ===== MONKEY-PATCH PARA UTF-8 NO FPDF.*?# ===== FIM DO MONKEY-PATCH =====\n?',
    re.DOTALL
)
codigo = padrao_mp.sub("", codigo)

# 3. Injeta o monkey-patch v2 logo após a criação do app
novo_mp = '''# ===== MONKEY-PATCH PARA UTF-8 NO FPDF (v2) =====
import os as _os_mp
_FONT_PATH_UTF8 = "C:/Windows/Fonts/arial.ttf"

if _os_mp.path.exists(_FONT_PATH_UTF8):
    try:
        from fpdf import FPDF as _FPDF_Original

        _original_set_font = _FPDF_Original.set_font

        def _set_font_utf8(self, family="helvetica", style="", size=0):
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
        print(f"[FPDF-UTF8] Erro no monkey-patch: {_e}")
# ===== FIM DO MONKEY-PATCH =====
'''

padrao_app = re.compile(r'(app\s*=\s*FastAPI\s*\([^)]*\))')
if padrao_app.search(codigo):
    codigo = padrao_app.sub(r'\1\n\n' + novo_mp, codigo, count=1)
    print("[OK] Monkey-patch v2 injetado após app = FastAPI().")
else:
    print("[ERRO] app = FastAPI() não encontrado.")
    exit()

# 4. Valida e salva
try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(r"pc_backend\main.py", "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo. Monkey-patch v2 está ativo.")
