import shutil
import re

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_isolando_botao_salvar")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove qualquer chamada acidental a exibirSelecionado ou excluirSelecionado dentro da função de salvar
# Vamos substituir o bloco inteiro da função salvarRelatorioConsolidado por uma versão limpa
padrao_funcao = r'(async\s+)?function salvarRelatorioConsolidado\s*\([^)]*\)\s*\{.*?\n\s*\}'
nova_funcao = '''async function salvarRelatorioConsolidado() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    const trimestre = document.getElementById('trimestre').value;
    const periodo = ano + '-' + tipo + '-' + trimestre;

    if (!confirm("Deseja realmente salvar este relatório consolidado no histórico?")) return;

    try {
        console.log("Chamando rota /salvar_relatorio_consolidado/" + periodo);
        
        const res = await fetch('/salvar_relatorio_consolidado/' + periodo, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!res.ok) {
            const texto = await res.text();
            throw new Error('HTTP ' + res.status + ': ' + texto.substring(0, 200));
        }
        
        const data = await res.json();
        console.log("Resposta do backend:", data);
        
        if (data.ok) {
            alert("Relatório salvo com sucesso no PostgreSQL!");
            // Recarrega a lista lateral sem chamar exibirSelecionado
            if (typeof carregarHistoricoConsolidado === 'function') {
                carregarHistoricoConsolidado();
            } else if (typeof carregarHistorico === 'function') {
                carregarHistorico();
            }
        } else {
            alert("Erro ao salvar: " + (data.mensagem || "Erro desconhecido"));
        }
    } catch (err) {
        console.error("Erro completo:", err);
        alert("Erro de conexão ao salvar: " + err.message);
    }
}'''

if re.search(padrao_funcao, html, re.DOTALL):
    html = re.sub(padrao_funcao, nova_funcao, html, count=1, flags=re.DOTALL)
    print("✅ Função 'salvarRelatorioConsolidado' isolada e corrigida.")
else:
    print("⚠️ Padrão da função não encontrado. Tentando abordagem alternativa...")
    # Abordagem alternativa: encontrar a função pelo nome e substituir manualmente
    idx = html.find("function salvarRelatorioConsolidado")
    if idx != -1:
        # Encontra o final da função
        i = html.find("{", idx)
        c = 1
        i += 1
        while i < len(html) and c > 0:
            if html[i] == "{": c += 1
            elif html[i] == "}": c -= 1
            i += 1
        html = html[:idx] + nova_funcao + html[i:]
        print("✅ Função substituída via abordagem alternativa.")
    else:
        print("❌ Função não encontrada.")

# 2. Garante que o botão "Confirmar e Salvar" chame a função correta
html = re.sub(r'onclick="[^"]*"', 'onclick="salvarRelatorioConsolidado()"', html, count=1)  # Apenas a primeira ocorrência (que é o botão)

# 3. Adiciona um log no console para verificar se o botão foi clicado
html = html.replace('onclick="salvarRelatorioConsolidado()"', 'onclick="console.log(\'Botão salvar clicado\'); salvarRelatorioConsolidado()"')

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ HTML corrigido e botão isolado.")
