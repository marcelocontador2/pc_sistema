import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# Corrigir todos os mojibakes nos nomes dos modulos
correcoes = {
    "An脙隆lise DFC": "Análise DFC",
    "An脙隆lise BP": "Análise BP",
    "An脙隆lise Patrimonial (DVP)": "Análise Patrimonial (DVP)",
    "An脙隆lise Or脙搂ament脙隆ria (BO)": "Análise Orçamentária (BO)",
    "An脙隆lise Financeira (BF)": "Análise Financeira (BF)",
    "An脙隆lise por Centro de Custos": "Análise por Centro de Custos",
    "Demonstra脙搂脙拢o das Muta脙搂脙碌es do PL (DMPL)": "Demonstração das Mutações do PL (DMPL)",
    "Demonstra脙搂脙拢o das Muta脙搂脙碌es do Patrim脙麓nio L脙颅quido (DMPL)": "Demonstração das Mutações do PL (DMPL)",
    "Integridade entre Demonstra脙搂脙碌es": "Integridade entre Demonstrações",
    "Confer脙陋ncia das Demonstra脙搂脙碌es": "Conferência das Demonstrações",
    "脙聜ndices de Liquidez": "Índices de Liquidez",
    "脙聜ndices": "Índices",
    "ÃÂndices de Liquidez": "Índices de Liquidez",
    "Ãndices de Liquidez": "Índices de Liquidez",
}

count = 0
for errado, certo in correcoes.items():
    if errado in texto:
        ocorrencias = texto.count(errado)
        texto = texto.replace(errado, certo)
        print(f"[OK] {ocorrencias}x: '{errado}' -> '{certo}'")
        count += ocorrencias

if count == 0:
    print("[AVISO] Nenhum mojibake encontrado.")
else:
    print(f"[OK] Total: {count} correcoes aplicadas.")

# Salvar
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
