import shutil, datetime, ast, os

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# PARTE 1: BACKEND (main.py)
# ============================================================
print("=" * 60)
print("PARTE 1: BACKEND (main.py)")
print("=" * 60)

back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_config_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se as rotas de configuracao ja existem
if "/api/configuracoes/entidade" in c:
    print("[AVISO] Rotas de configuracao ja existem no main.py. Pulando.")
else:
    # Encontra um ponto seguro para inserir (antes da ultima linha do arquivo ou antes do if __name__)
    idx = c.find("if __name__")
    if idx == -1:
        idx = len(c) - 500  # fallback: insere perto do final
    
    bloco_backend = '''

# ============================================================
# ROTAS DE CONFIGURACOES (CADASTRO DA ENTIDADE)
# ============================================================

@app.get("/api/configuracoes/entidade")
async def obter_entidade():
    import sqlite3, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT,
        nome_fantasia TEXT,
        cnpj TEXT,
        endereco TEXT,
        email TEXT,
        telefone TEXT,
        contador_nome TEXT,
        contador_crc TEXT,
        contador_uf TEXT,
        contador_cpf TEXT,
        contador_email TEXT,
        data_atualizacao TEXT
    )""")
    conn.commit()
    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {
            "razao_social": "", "nome_fantasia": "", "cnpj": "", "endereco": "",
            "email": "", "telefone": "", "contador_nome": "", "contador_crc": "",
            "contador_uf": "", "contador_cpf": "", "contador_email": ""
        }
    
    return {
        "razao_social": row[1] or "",
        "nome_fantasia": row[2] or "",
        "cnpj": row[3] or "",
        "endereco": row[4] or "",
        "email": row[5] or "",
        "telefone": row[6] or "",
        "contador_nome": row[7] or "",
        "contador_crc": row[8] or "",
        "contador_uf": row[9] or "",
        "contador_cpf": row[10] or "",
        "contador_email": row[11] or ""
    }

@app.post("/api/configuracoes/entidade")
async def salvar_entidade(request: Request):
    import sqlite3, json
    from datetime import datetime
    try:
        body = await request.json()
    except Exception:
        return {"ok": False, "mensagem": "Dados invalidos."}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT
    )""")
    
    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Remove registro anterior e insere novo (mantem apenas 1)
    cursor.execute("DELETE FROM configuracoes_entidade")
    cursor.execute("""INSERT INTO configuracoes_entidade 
        (razao_social, nome_fantasia, cnpj, endereco, email, telefone, 
         contador_nome, contador_crc, contador_uf, contador_cpf, contador_email, data_atualizacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        body.get("razao_social", ""),
        body.get("nome_fantasia", ""),
        body.get("cnpj", ""),
        body.get("endereco", ""),
        body.get("email", ""),
        body.get("telefone", ""),
        body.get("contador_nome", ""),
        body.get("contador_crc", ""),
        body.get("contador_uf", ""),
        body.get("contador_cpf", ""),
        body.get("contador_email", ""),
        data_agora
    ))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Configuracoes salvas com sucesso!"}

@app.get("/configuracoes")
async def serve_configuracoes():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "configuracoes.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

'''
    
    c = c[:idx] + bloco_backend + c[idx:]
    open(back_path, "w", encoding="utf-8").write(c)
    
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] Rotas de configuracao inseridas no main.py e sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_config_{ts}", back_path)
        print("[OK] Backup restaurado.")
        exit(1)

# ============================================================
# PARTE 2: FRONTEND (configuracoes.html)
# ============================================================
print("\n" + "=" * 60)
print("PARTE 2: FRONTEND (configuracoes.html)")
print("=" * 60)

arq_front = "pc_frontend/configuracoes.html"
if os.path.exists(arq_front):
    print("[AVISO] configuracoes.html ja existe. Pulando criacao.")
else:
    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Configuracoes - Cadastro da Entidade</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .top-bar { display: flex; gap: 10px; margin-bottom: 20px; align-items: center; }
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; color: white; }
        .btn-voltar { background: #f0ad4e; }
        .btn-salvar { background: #28a745; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 900px; margin: 0 auto; }
        h1 { color: #003366; margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #003366; font-size: 16px; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group.full { grid-column: span 2; }
        label { font-size: 12px; font-weight: bold; color: #555; margin-bottom: 5px; }
        input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #003366; }
        .msg-sucesso { background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin-bottom: 15px; display: none; }
    </style>
</head>
<body>

    <div class="top-bar">
        <button class="btn btn-voltar" onclick="window.location.href='/'">&larr; Voltar</button>
    </div>

    <div class="container">
        <h1>Configuracoes - Cadastro da Entidade</h1>
        <div id="msg-sucesso" class="msg-sucesso">Configuracoes salvas com sucesso!</div>

        <h2>Dados da Entidade</h2>
        <div class="form-grid">
            <div class="form-group full">
                <label>Razao Social</label>
                <input type="text" id="razao_social" placeholder="Ex: Conselho Federal de Enfermagem">
            </div>
            <div class="form-group">
                <label>Nome Fantasia</label>
                <input type="text" id="nome_fantasia" placeholder="Ex: COFEN">
            </div>
            <div class="form-group">
                <label>CNPJ</label>
                <input type="text" id="cnpj" placeholder="00.000.000/0000-00">
            </div>
            <div class="form-group full">
                <label>Endereco</label>
                <input type="text" id="endereco" placeholder="Rua, numero, bairro, cidade - UF">
            </div>
            <div class="form-group">
                <label>E-mail</label>
                <input type="email" id="email" placeholder="contato@cofen.gov.br">
            </div>
            <div class="form-group">
                <label>Telefone</label>
                <input type="text" id="telefone" placeholder="(61) 0000-0000">
            </div>
        </div>

        <h2>Dados do Contador</h2>
        <div class="form-grid">
            <div class="form-group full">
                <label>Nome do Contador</label>
                <input type="text" id="contador_nome" placeholder="Nome completo">
            </div>
            <div class="form-group">
                <label>Registro CRC</label>
                <input type="text" id="contador_crc" placeholder="Ex: 066005-O">
            </div>
            <div class="form-group">
                <label>UF do CRC</label>
                <input type="text" id="contador_uf" placeholder="Ex: DF" maxlength="2">
            </div>
            <div class="form-group">
                <label>CPF do Contador</label>
                <input type="text" id="contador_cpf" placeholder="000.000.000-00">
            </div>
            <div class="form-group">
                <label>E-mail do Contador</label>
                <input type="email" id="contador_email" placeholder="contador@cofen.gov.br">
            </div>
        </div>

        <div style="margin-top: 30px; text-align: right;">
            <button class="btn btn-salvar" onclick="salvarConfiguracoes()">Salvar Configuracoes</button>
        </div>
    </div>

    <script>
        function carregarConfiguracoes() {
            fetch('/api/configuracoes/entidade')
                .then(r => r.json())
                .then(data => {
                    for (const [key, value] of Object.entries(data)) {
                        const el = document.getElementById(key);
                        if (el) el.value = value || '';
                    }
                })
                .catch(e => console.error("Erro ao carregar:", e));
        }

        function salvarConfiguracoes() {
            const campos = [
                'razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'email', 'telefone',
                'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'
            ];
            const dados = {};
            campos.forEach(c => {
                const el = document.getElementById(c);
                if (el) dados[c] = el.value;
            });

            fetch('/api/configuracoes/entidade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(dados)
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    const msg = document.getElementById('msg-sucesso');
                    msg.style.display = 'block';
                    setTimeout(() => { msg.style.display = 'none'; }, 3000);
                } else {
                    alert("Erro: " + (data.mensagem || "Falha ao salvar."));
                }
            })
            .catch(e => alert("Erro de conexao."));
        }

        document.addEventListener('DOMContentLoaded', carregarConfiguracoes);
    </script>
</body>
</html>
'''
    open(arq_front, "w", encoding="utf-8").write(html)
    print("[OK] Página configuracoes.html criada com sucesso.")

# ============================================================
# PARTE 3: MENU LATERAL (index.html e normas.html)
# ============================================================
print("\n" + "=" * 60)
print("PARTE 3: MENU LATERAL (index.html e normas.html)")
print("=" * 60)

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    if not os.path.exists(arq):
        continue
    
    shutil.copy2(arq, f"{arq}.bak_config_{ts}")
    c = open(arq, encoding="utf-8", errors="ignore").read()
    
    if 'href="/configuracoes"' in c:
        print(f"[AVISO] {arq} ja tem link para configuracoes.")
        continue
    
    # Procura o link de "Base Legal" ou "Importar Relatorios" para inserir depois
    idx = c.find('href="/base_legal"')
    if idx == -1:
        idx = c.find('href="/importar"')
    
    if idx != -1:
        # Encontra o fim do <li> do link encontrado
        end_li = c.find('</li>', idx)
        if end_li != -1:
            novo_li = '\n    <li><a href="/configuracoes" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Configuracoes</a></li>'
            c = c[:end_li+5] + novo_li + c[end_li+5:]
            open(arq, "w", encoding="utf-8").write(c)
            print(f"[OK] {arq} - link Configuracoes adicionado.")
    else:
        print(f"[AVISO] {arq} - nao encontrei ponto de insercao.")

print("\n" + "=" * 60)
print("CONCLUIDO!")
print("=" * 60)
print(f"Backup do main.py salvo como: main.py.bak_config_{ts}")
print("Para testar: reinicie o servidor e acesse /configuracoes")
