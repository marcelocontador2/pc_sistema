import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Dicionário de correções de duplo encoding (mojibake) comum
correcoes = {
    "Ã¡": "á", "Ã¢": "â", "Ã£": "ã", "Ã¤": "ä",
    "Ã©": "é", "Ãª": "ê", "Ã«": "ë",
    "Ã­": "í", "Ã®": "î", "Ã¯": "ï",
    "Ã³": "ó", "Ã´": "ô", "Ãµ": "õ", "Ã¶": "ö",
    "Ãº": "ú", "Ã»": "û", "Ã¼": "ü",
    "Ã§": "ç", "Ã±": "ñ",
    "Ã": "Á", "Ã‰": "É", "Ã": "Í", "Ã“": "Ó", "Ãš": "Ú",
    "Ã‡": "Ç"
}

# Corrige o dicionário de nomes amigáveis e a tabela do DMPL/Panorama
texto_corrigido = texto
for errado, certo in correcoes.items():
    texto_corrigido = texto_corrigido.replace(errado, certo)

# Corrige o "ÃÂndices" (que é o Í com dupla corrupção)
texto_corrigido = texto_corrigido.replace("ÃÂndices", "Índices")
texto_corrigido = texto_corrigido.replace("Ãndices", "Índices")

# Corrige os nomes das tabelas que estavam errados no dicionário
texto_corrigido = texto_corrigido.replace('"panorama": "historico_panorama",', '"panorama": "historico_panorama_resultados",')
texto_corrigido = texto_corrigido.replace('"integridade": "historico_integridade_matriz",', '"integridade": "historico_integridade",')
texto_corrigido = texto_corrigido.replace('"dmpl": "historico_analise_dmpl"', '"dmpl": "historico_dmpl"')

arquivo.write_text(texto_corrigido, encoding="utf-8")
print("[OK] Nomes amigáveis e tabelas corrigidos no main_legado.py.")
