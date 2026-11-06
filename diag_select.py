import glob, os

# Procura em todos os HTMLs e JS o select de tipo de relatorio
for arq in glob.glob("pc_frontend/**/*.*", recursive=True):
    if not arq.endswith((".html", ".js")):
        continue
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    
    # Procura por "tipo" ou "relatorio" em selects
    if '<select' in c and ('tipo' in c.lower() or 'relatorio' in c.lower()):
        # Mostra os selects que tem "tipo" ou "relatorio"
        import re
        for m in re.finditer(r'<select[^>]*>.*?</select>', c, re.DOTALL):
            trecho = m.group(0)
            if 'tipo' in trecho.lower() or 'relatorio' in trecho.lower() or 'Balanco' in trecho or 'BALANCO' in trecho:
                print(f"\nArquivo: {arq}")
                print(trecho[:800])
                print("-" * 70)
