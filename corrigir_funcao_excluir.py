import re, shutil, datetime

arq = r"pc_frontend\analise_comparativo_despesas.html"
shutil.copy2(arq, f"{arq}.bak_fix_excluir_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Vamos encontrar o bloco da função excluirSelecionado e substituir por uma versão limpa
# Estratégia: pegar do "function excluirSelecionado" até o "function gerarPDF" (a próxima função)
idx_ini = html.find("function excluirSelecionado")
idx_fim = html.find("function gerarPDF", idx_ini)

if idx_ini != -1 and idx_fim != -1:
    funcao_limpa = '''function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            fetch("/excluir_multiplos_comparativo_despesas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ids: ids })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    carregarHistorico();
                } else {
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }
            })
            .catch(e => alert("Erro de conexão ao excluir."));
        }

        '''
    
    html = html[:idx_ini] + funcao_limpa + html[idx_fim:]
    
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Função excluirSelecionado substituída por versão limpa e completa.")
else:
    print(f"[ERRO] Não foi possível encontrar os limites da função. ini={idx_ini}, fim={idx_fim}")

# Verificação final
with open(arq, "r", encoding="utf-8") as f:
    html2 = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html2, re.DOTALL | re.IGNORECASE)
if scripts:
    s = scripts[0]
    abre = s.count('{')
    fecha = s.count('}')
    print(f"\n=== VERIFICAÇÃO PÓS-CORREÇÃO ===")
    print(f"Chaves no bloco: {{ {abre} x }} {fecha}")
    if abre == fecha:
        print("[OK] Chaves balanceadas! O JavaScript agora vai executar corretamente.")
    else:
        print(f"[ALERTA] Ainda há desbalanceamento de {abre - fecha} chaves.")

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor.")
print("2. Aperte Ctrl+Shift+R no navegador na tela de Despesas.")
print("3. O histórico deve carregar.")
