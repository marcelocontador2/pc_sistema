import re
import shutil

# --- PARTE 1: Ajustar o Backend (main.py) para priorizar o histórico do PostgreSQL ---
caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_prioriza_historico")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo_main = f.read()

# Localiza a função api_integridade_matriz_calcular e substitui
idx_inicio = conteudo_main.find('async def api_integridade_matriz_calcular(periodo: str):')
if idx_inicio != -1:
    i = conteudo_main.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo_main) and c > 0:
        if conteudo_main[i] == "{": c += 1
        elif conteudo_main[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''async def api_integridade_matriz_calcular(periodo: str):
    import json
    try:
        # Tenta primeiro buscar o último histórico salvo no PostgreSQL
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado_json FROM historico_integridade_matriz ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            # Se encontrou histórico, retorna exatamente o JSON salvo
            return json.loads(row[0])
            
        # Se não encontrou, tenta calcular via CSVs (fallback)
        from .matriz_integridade import gerar_matriz
        dados = gerar_matriz(periodo)
        return dados
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''
    conteudo_main = conteudo_main[:idx_inicio] + nova_funcao + conteudo_main[i:]
    
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo_main)
    print("✅ Backend (main.py) atualizado para priorizar o histórico do PostgreSQL!")
else:
    print("❌ Função 'api_integridade_matriz_calcular' não encontrada no main.py.")

# --- PARTE 2: Ajustar o Frontend (integridade.html) ---
caminho_html = "pc_frontend/integridade.html"
shutil.copy(caminho_html, caminho_html + ".bak_prioriza_historico")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a função verificarEGerar
idx_v = html.find("async function verificarEGerar(")
if idx_v != -1:
    i = html.find("{", idx_v)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_v = '''async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Buscando dados no banco (PostgreSQL)...</div>';

        try {
            // Busca os dados (o backend agora prioriza o histórico salvo)
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            const data = await res.json();

            if (data.erro) {
                throw new Error(data.mensagem || "Erro desconhecido no backend.");
            }

            // Renderiza a matriz na tela
            dadosAtuais = data;
            renderizarMatriz(data, container);
            
            // Atualiza a lista lateral de históricos
            carregarHistorico();

        } catch (err) {
            console.error(err);
            if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">
                <strong>Erro ao carregar matriz:</strong> ${err.message}
            </div>`;
        }
    }'''
    html = html[:idx_v] + nova_v + html[i:]
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Frontend (integridade.html) atualizado para exibir o histórico do PostgreSQL!")
else:
    print("❌ Função 'verificarEGerar' não encontrada no integridade.html.")
