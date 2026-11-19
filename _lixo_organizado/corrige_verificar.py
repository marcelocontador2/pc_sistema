import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Corrige a funcao verificarDados para usar os campos corretos (total_faltando -> len(faltando))
antigo = '''            fetch('/api/relatorio_consolidado/' + periodo)
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'ok') {
                        statusBox.className = 'status-box';
                        statusBox.innerHTML = "<strong>Todos os modulos estao prontos para consolidar!</strong><br>Encontrados: " + data.total_encontrados + " / " + data.total_modulos;
                    } else {
                        statusBox.className = 'status-box erro';
                        statusBox.innerHTML = "<strong>Atencao:</strong> " + data.total_faltando + " modulo(s) faltando.";
                    }
                })'''

novo = '''            fetch('/api/relatorio_consolidado/' + periodo)
                .then(r => r.json())
                .then(data => {
                    var totalEncontrados = (data.encontrados || []).length;
                    var totalFaltando = (data.faltando || []).length;
                    if (totalFaltando === 0) {
                        statusBox.className = 'status-box';
                        statusBox.innerHTML = "<strong>Todos os modulos estao prontos para consolidar!</strong><br>Encontrados: " + totalEncontrados + " / " + (totalEncontrados + totalFaltando);
                    } else {
                        statusBox.className = 'status-box erro';
                        statusBox.innerHTML = "<strong>Atencao:</strong> " + totalFaltando + " modulo(s) faltando.";
                    }
                })'''

if antigo in texto:
    texto = texto.replace(antigo, novo, 1)
    print("[OK] Funcao verificarDados corrigida.")
else:
    print("[AVISO] Nao encontrei o bloco exato. Tentando substituicao mais tolerante...")
    import re
    # Fallback: troca so os campos problematicos
    texto = texto.replace('data.total_encontrados', '(data.encontrados || []).length')
    texto = texto.replace('data.total_faltando', '(data.faltando || []).length')
    texto = texto.replace('data.total_modulos', '((data.encontrados || []).length + (data.faltando || []).length)')
    print("[OK] Campos substituidos via fallback.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
