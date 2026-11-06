import re, shutil, sys, datetime

ARQUIVO = r"pc_backend\main.py"
BACKUP = f"pc_backend\\main_backup_liquidez2_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(ARQUIVO, BACKUP)
print(f"[OK] Backup: {BACKUP}\n")

# ---------- 1) DIAGNOSTICO: mostrar CSV do BP ----------
sys.path.insert(0, "pc_backend")
from matriz_integridade import _ler_linhas, _get_csv

caminho = _get_csv("BALANCO_PATRIMONIAL", "2026-TRIMESTRE-3")
print(f"=== CSV: {caminho} ===")
if not caminho:
    print("[ERRO] CSV nao encontrado para 2026-TRIMESTRE-3")
    sys.exit(1)

linhas = _ler_linhas(caminho)
print(f"Total de linhas: {len(linhas)}\n")

# Procura termos relevantes e mostra onde casaram
termos = ["ATIVO", "PASSIVO", "PATRIM", "REALIZ", "CIRCULANTE", "TOTAL"]
print("=== Linhas do CSV que contem ATIVO/PASSIVO/PATRIM/REALIZ/TOTAL ===")
for i, p in enumerate(linhas):
    txt = " | ".join(str(c)[:50] for c in p[:5])
    up = txt.upper()
    if any(t in up for t in termos):
        print(f"{i:4}: {txt}")

# ---------- 2) PATCH: melhorar o buscar() e fallbacks ----------
with open(ARQUIVO, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 2a) Adiciona normalizacao sem acento dentro do buscar()
old_buscar = '''    def buscar(*termos):
        """Retorna o primeiro valor > 0 encontrado para qualquer um dos termos (col 0=Ativo, 3=Passivo)."""
        for termo in termos:
            termo_upper = termo.upper()
            for p in l_bp:
                for col_espec in (0, 3):
                    if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except Exception:
                                pass
        return 0.0'''

new_buscar = '''    def _norm(s):
        import unicodedata
        s = unicodedata.normalize("NFKD", str(s))
        return "".join(c for c in s if not unicodedata.combining(c)).upper().strip()

    def buscar(*termos):
        """Retorna o primeiro valor > 0 encontrado para qualquer um dos termos (col 0=Ativo, 3=Passivo)."""
        for termo in termos:
            termo_norm = _norm(termo)
            for p in l_bp:
                for col_espec in (0, 3):
                    if len(p) > col_espec and termo_norm in _norm(p[col_espec]):
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except Exception:
                                pass
        return 0.0'''

if old_buscar not in conteudo:
    print("\n[ERRO] Nao achei o bloco 'def buscar(*termos):' atual. Abortando.")
    sys.exit(1)
conteudo = conteudo.replace(old_buscar, new_buscar, 1)
print("\n[OK] buscar() agora ignora acentos")

# 2b) Adiciona termos alternativos na busca
old_termos = '''    caixa = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ativo_circulante = buscar("ATIVO CIRCULANTE")
    estoques = buscar("ESTOQUES")
    realizavel_lp = buscar("REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO")
    ativo_nao_circulante = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE")
    imobilizado = buscar("IMOBILIZADO")
    passivo_circulante = buscar("PASSIVO CIRCULANTE")
    passivo_nao_circulante = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE")
    passivo_total = buscar("PASSIVO TOTAL", "TOTAL DO PASSIVO")
    ativo_total = buscar("ATIVO TOTAL", "TOTAL DO ATIVO")
    patrimonio_liquido = buscar("PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO")'''

new_termos = '''    caixa = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ativo_circulante = buscar("ATIVO CIRCULANTE")
    estoques = buscar("ESTOQUES")
    realizavel_lp = buscar("REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO", "REALIZAVEL LP", "ATIVO REALIZAVEL")
    ativo_nao_circulante = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE", "ATIVO NAO CIRCULANTE", "ANC")
    imobilizado = buscar("IMOBILIZADO", "IMOBILIZADO LIQUIDO")
    passivo_circulante = buscar("PASSIVO CIRCULANTE")
    passivo_nao_circulante = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE", "PASSIVO NAO CIRCULANTE", "PNC")
    passivo_total = buscar("PASSIVO TOTAL", "TOTAL DO PASSIVO", "TOTAL PASSIVO")
    ativo_total = buscar("ATIVO TOTAL", "TOTAL DO ATIVO", "TOTAL ATIVO")
    patrimonio_liquido = buscar("PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO", "PATRIMONIO SOCIAL", "PL")'''

if old_termos not in conteudo:
    print("\n[ERRO] Nao achei o bloco de termos atual. Abortando.")
    sys.exit(1)
conteudo = conteudo.replace(old_termos, new_termos, 1)
print("[OK] Termos alternativos adicionados")

# 2c) Fallbacks robustos para totais ausentes
old_fallback = '''    if not ativo_total and ativo_circulante and ativo_nao_circulante:
        ativo_total = ativo_circulante + ativo_nao_circulante
    if not passivo_total and passivo_circulante and passivo_nao_circulante:
        passivo_total = passivo_circulante + passivo_nao_circulante
    if not patrimonio_liquido and ativo_total and passivo_total:
        patrimonio_liquido = ativo_total - passivo_total'''

new_fallback = '''    # Fallbacks robustos quando as linhas totais nao existem no CSV
    if not ativo_nao_circulante and imobilizado:
        ativo_nao_circulante = imobilizado
    if not ativo_total:
        ativo_total = (ativo_circulante or 0.0) + (ativo_nao_circulante or 0.0) + (realizavel_lp or 0.0)
    if not passivo_total and passivo_circulante and passivo_nao_circulante:
        passivo_total = passivo_circulante + passivo_nao_circulante
    if not patrimonio_liquido and ativo_total and passivo_total:
        patrimonio_liquido = ativo_total - passivo_total'''

if old_fallback not in conteudo:
    print("\n[ERRO] Nao achei o bloco de fallback atual. Abortando.")
    sys.exit(1)
conteudo = conteudo.replace(old_fallback, new_fallback, 1)
print("[OK] Fallbacks robustos aplicados")

# ---------- 3) Validar e salvar ----------
try:
    compile(conteudo, ARQUIVO, "exec")
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    sys.exit(1)

with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(conteudo)
print(f"[OK] main.py atualizado ({len(conteudo):,} chars)\n")
print("=== PROXIMO PASSO ===")
print("1. Ctrl+C no servidor uvicorn")
print("2. Suba de novo:  cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Teste:         .\\pc_venv\\Scripts\\python.exe testar_api_liquidez.py")
