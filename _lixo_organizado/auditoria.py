import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# Extrai todos os blocos <script>...</script>
blocos = re.findall(r'<script>(.*?)</script>', texto, re.DOTALL)

print(f"[INFO] Encontrados {len(blocos)} blocos de <script> no HTML.")

# Salva cada bloco em um arquivo separado para auditoria
for i, bloco in enumerate(blocos):
    nome = f"audit_script_{i+1}.js"
    Path(nome).write_text(bloco, encoding="utf-8")
    print(f"[INFO] Bloco {i+1} salvo em {nome} ({len(bloco)} caracteres)")

# Verifica se ha erros obvios de sintaxe nos blocos
for i, bloco in enumerate(blocos):
    # Conta chaves, parenteses e colchetes
    abre_chave = bloco.count("{")
    fecha_chave = bloco.count("}")
    abre_parent = bloco.count("(")
    fecha_parent = bloco.count(")")
    abre_colch = bloco.count("[")
    fecha_colch = bloco.count("]")
    
    print(f"\n[BL OCO {i+1}]")
    print(f"  Chaves: {abre_chave} abre / {fecha_chave} fecha -> {'OK' if abre_chave == fecha_chave else 'ERRO'}")
    print(f"  Parenteses: {abre_parent} abre / {fecha_parent} fecha -> {'OK' if abre_parent == fecha_parent else 'ERRO'}")
    print(f"  Colchetes: {abre_colch} abre / {fecha_colch} fecha -> {'OK' if abre_colch == fecha_colch else 'ERRO'}")
    
    # Procura por "disabled" ou "onclick" malformados
    if "function marcarTodos" in bloco:
        print("  [OK] Funcao marcarTodos encontrada.")
    if "function excluirSelecionados" in bloco:
        print("  [OK] Funcao excluirSelecionados encontrada.")
    if "function atualizarBotao" in bloco:
        print("  [OK] Funcao atualizarBotao encontrada.")
    if "chk-historico" in bloco:
        print("  [OK] Classe 'chk-historico' encontrada.")
    
    # Procura por erros comuns
    if "async" in bloco and "await" not in bloco:
        print("  [AVISO] 'async' sem 'await'.")
    if "=>" in bloco:
        print("  [INFO] Arrow functions encontradas (pode ser problema se o navegador for antigo).")
