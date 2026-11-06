import re, shutil, datetime

arq_html = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arq_html, f"{arq_html}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Corrige a função verificarDados para retirar o "º" do valor
old_func = """const valor = document.getElementById('periodo_valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;"""

new_func = """const valor = document.getElementById('periodo_valor').value;
            // Remove o º do valor (ex: "3º" vira "3")
            const valor_limpo = valor.replace('º', '').trim();
            const periodo = `${ano}-${tipo}-${valor_limpo}`;"""

if old_func in html:
    html = html.replace(old_func, new_func)
    print("[OK] Função verificarDados corrigida para remover o 'º' do período.")
else:
    print("[AVISO] Não encontrei o bloco exato da função verificarDados.")

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor (só mudou o HTML).")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados novamente.")
