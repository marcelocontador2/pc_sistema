import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_carregar_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Pega a funcao salvarMatriz atual
idx = c.find("async function salvarMatriz()")
if idx != -1:
    fim = c.find("}", idx) + 1
    # Substitui a funcao inteira por uma versao que atualiza a lista
    antigo_bloco = c[idx:fim]
    
    novo_bloco = '''async function salvarMatriz() {
        const btn = document.getElementById('btn-confirmar');
        const periodo = btn.getAttribute("data-periodo");
        btn.innerText = "Salvando..."; btn.disabled = true;
        try {
            const response = await fetch("/salvar_integridade_matriz/" + periodo, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ justificativas: window.justificativasSalvas || {} })
            });
            const data = await response.json();
            
            if (data.ok) {
                alert("Matriz e justificativas salvas com sucesso!");
                carregarHistorico(); // <--- AQUI atualiza a lista lateral
            } else {
                alert("Erro: " + (data.mensagem || "Falha ao salvar."));
            }
        } catch (e) { 
            alert("Erro de conexao ao salvar."); 
        } finally {
            btn.innerText = "Confirmar e Salvar"; btn.disabled = false;
        }
    }'''
    
    c = c.replace(antigo_bloco, novo_bloco)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao salvarMatriz atualizada no frontend.")
else:
    print("[ERRO] Funcao salvarMatriz nao encontrada no HTML.")
