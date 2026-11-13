import shutil

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_historico_lista")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Corrigir a rota que lista o histórico para usar PostgreSQL
idx_listar = conteudo.find('def listar_integridade_matriz():')
if idx_listar != -1:
    i = conteudo.find("{", idx_listar)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    nova_listar = '''def listar_integridade_matriz():
    import json
    import psycopg2
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_integridade_matriz ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        resultado = []
        for r in rows:
            resultado.append({
                "id": r[0],
                "periodo": r[1],
                "data_geracao": r[2],
                "dados": r[3]
            })
        return Response(content=json.dumps(resultado), media_type="application/json")
    except Exception as e:
        return Response(content=json.dumps({"erro": True, "mensagem": str(e)}), media_type="application/json")'''
    
    conteudo = conteudo[:idx_listar] + nova_listar + conteudo[i:]
    print("✅ Rota de listar histórico atualizada para PostgreSQL!")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# 2. Ajuste no Frontend para forçar a atualização da lista após salvar
caminho_html = "pc_frontend/integridade.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_lista_refresh")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a função carregarHistorico para garantir que use o fetch certo e atualize o DOM
idx_carregar = html.find("function carregarHistorico()")
if idx_carregar != -1:
    i = html.find("{", idx_carregar)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_carregar = '''function carregarHistorico() {
        const list = document.getElementById('lista-historico');
        if (!list) return;
        list.innerHTML = '<li class="loading">Carregando histórico...</li>';
        
        fetch(`/historico_integridade_matriz?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                list.innerHTML = '';
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(h => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <input type="checkbox" value="${h.id}">
                            <span>Período: ${h.periodo} | Gerado em: ${h.data_geracao || 'N/A'}</span>
                        `;
                        list.appendChild(li);
                    });
                } else {
                    list.innerHTML = '<li>Nenhum histórico salvo.</li>';
                }
            })
            .catch(err => {
                list.innerHTML = '<li>Erro ao carregar histórico.</li>';
                console.error(err);
            });
    }'''
    
    html = html[:idx_carregar] + nova_carregar + html[i:]
    print("✅ Função carregarHistorico no frontend atualizada!")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Correções aplicadas! Reinicie o servidor Python e teste novamente.")
