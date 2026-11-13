import re
import shutil

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_botao_global")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Primeiro, vamos remover qualquer versão antiga da função (para não duplicar)
padrao_remover = r'(?:async\s+)?function salvarRelatorioConsolidado\s*\([^)]*\)\s*\{.*?\n\s*\}'
html = re.sub(padrao_remover, '', html, flags=re.DOTALL)

# 2. Agora, vamos inserir a versão correta no FINAL do último <script> (escopo global)
# Encontra o último fechamento de </script>
idx_ultimo_script = html.rfind('</script>')

if idx_ultimo_script != -1:
    nova_funcao = '''
    // --- FUNÇÃO GLOBAL DE SALVAR RELATÓRIO CONSOLIDADO ---
    async function salvarRelatorioConsolidado() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        if (!confirm("Deseja realmente salvar este relatório consolidado no histórico?")) return;

        try {
            console.log("Chamando rota /salvar_relatorio_consolidado/" + periodo);
            
            const res = await fetch(`/salvar_relatorio_consolidado/${periodo}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!res.ok) {
                const texto = await res.text();
                throw new Error(`HTTP ${res.status}: ${texto.substring(0, 200)}`);
            }
            
            const data = await res.json();
            console.log("Resposta do backend:", data);
            
            if (data.ok) {
                alert("Relatório salvo com sucesso no PostgreSQL!");
                if (typeof carregarHistorico === 'function') {
                    carregarHistorico();
                } else {
                    window.location.reload();
                }
            } else {
                alert("Erro ao salvar: " + (data.mensagem || "Erro desconhecido"));
            }
        } catch (err) {
            console.error("Erro completo:", err);
            alert("Erro de conexão ao salvar: " + err.message);
        }
    }
    // --- FIM DA FUNÇÃO ---
    '''
    
    html = html[:idx_ultimo_script] + nova_funcao + html[idx_ultimo_script:]
    print("✅ Função 'salvarRelatorioConsolidado' movida para o escopo global e com 'async'.")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML corrigido. Reinicie o servidor e teste o botão.")
