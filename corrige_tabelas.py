import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Volta para os nomes corretos
texto = texto.replace('"panorama": "historico_panorama_resultados",', '"panorama": "historico_panorama",')
texto = texto.replace('"dmpl": "historico_dmpl"', '"dmpl": "historico_analise_dmpl"')

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Nomes de tabelas corrigidos (panorama -> historico_panorama, dmpl -> historico_analise_dmpl).")
