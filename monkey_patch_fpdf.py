import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fallback_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

fonte_ok = "C:/Windows/Fonts/arial.ttf"
if not os.path.exists(fonte_ok):
    print("[ERRO] arial.ttf não encontrado.")
    exit()

# Estratégia: no INÍCIO da aplicação, após criar a instância FastAPI, injeta o fallback global.
# Vamos localizar a linha "app = FastAPI()" (ou similar) e adicionar o monkey-patch do FPDF.

# Primeiro, encontra a criação do app
padrao_app = re.compile(r'^app\s*=\s*FastAPI\s*\([^)]*\)', re.MULTILINE)
match_app = padrao_app.search(main_code)
if not match_app:
    print("[ERRO] 'app = FastAPI()' não encontrado.")
    exit()

injecao = f'''
# ===== MONKEY-PATCH PARA UTF-8 NO FPDF =====
# Intercepta a criação de qualquer FPDF() e registra a fonte Arial (TTF) como fallback.
try:
    from fpdf import FPDF as _FPDF_Original
    import fpdf as _fpdf_module

    _FONT_PATH_UTF8 = r"{fonte_ok}"

    class _FPDFComUTF8(_FPDF_Original):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                if not self.fonts:
                    pass  # ainda não há fontes carregadas
                self.add_font("ArialUTF8", "", _FONT_PATH_UTF8, uni=True)
                self.add_font("ArialUTF8", "B", _FONT_PATH_UTF8, uni=True)
                self.add_font("ArialUTF8", "I", _FONT_PATH_UTF8, uni=True)
                if hasattr(self, "set_fallback_fonts"):
                    self.set_fallback_fonts(["ArialUTF8"], exact_match=False)
            except Exception as _e:
                print(f"[FPDF-UTF8] Aviso ao registrar fallback: {{_e}}")

    # Substitui a referência global de FPDF
    _fpdf_module.FPDF = _FPDFComUTF8
    import sys as _sys
    for _mod_name in list(_sys.modules.keys()):
        if _mod_name.startswith("main") or _mod_name == "__main__":
            continue
except Exception as _err:
    print(f"[FPDF-UTF8] Erro no monkey-patch: {{_err}}")
# ===== FIM DO MONKEY-PATCH =====
'''

# Injeta logo APÓS "app = FastAPI()"
main_code = main_code[:match_app.end()] + "\n" + injecao + main_code[match_app.end():]

# Valida sintaxe
try:
    compile(main_code, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Monkey-patch UTF-8 injetado globalmente no FPDF.")
