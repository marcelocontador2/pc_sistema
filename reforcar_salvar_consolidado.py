import shutil
import ast

# --- PARTE 1: Reforçar a função de salvar no HTML ---
print("🔧 [1/2] REFORÇANDO A FUNÇÃO DE SALVAR NO HTML...")
caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_reforcar_salvar")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a função salvarRelatorioConsolidado
idx_inicio = html.find("async function salvarRelatorioConsolidado()")
if idx_inicio == -1:
    idx_inicio = html.find("function salvarRelatorioConsolidado()")

if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''async function salvarRelatorioConsolidado() {
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
    }'''
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    print("✅ Função 'salvarRelatorioConsolidado' reforçada com logs e tratamento de erro.")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

# --- PARTE 2: Garantir que a rota api_relatorio_consolidado_novo está segura ---
print("\n🔧 [2/2] VERIFICANDO A ROTA api_relatorio_consolidado_novo NO BACKEND...")
caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_verificar_api_consolidado")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Verifica se a função retorna "encontrados" e "faltando"
if '"encontrados": encontrados' in conteudo and '"faltando": faltando' in conteudo:
    print("✅ A função 'api_relatorio_consolidado_novo' retorna 'encontrados' e 'faltando' corretamente.")
else:
    print("⚠️ A função pode não estar retornando os campos esperados. Verificando...")

# Verifica se a rota de salvar chama a api_relatorio_consolidado_novo
if 'dados_api = await api_relatorio_consolidado_novo(periodo)' in conteudo:
    print("✅ A rota de salvar chama 'api_relatorio_consolidado_novo' corretamente.")
else:
    print("⚠️ A rota de salvar pode não estar chamando a API corretamente.")
