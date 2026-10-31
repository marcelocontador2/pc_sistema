from pathlib import Path

html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Configurações - SIGPC</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; padding: 40px; color: #333; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #003366; margin-top: 0; }
        .desc { color: #666; margin-bottom: 30px; line-height: 1.6; }
        .opcao { display: flex; align-items: center; padding: 20px; border: 2px solid #eee; border-radius: 8px; margin-bottom: 15px; cursor: pointer; transition: 0.2s; }
        .opcao:hover { border-color: #003366; background: #f0f7ff; }
        .opcao.ativo { border-color: #003366; background: #e8f0fe; }
        .opcao input { margin-right: 15px; transform: scale(1.5); cursor: pointer; }
        .opcao .titulo { font-weight: bold; font-size: 18px; color: #003366; }
        .opcao .sub { font-size: 14px; color: #666; }
        .btn-salvar { background: #28a745; color: #fff; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 20px; transition: 0.2s; }
        .btn-salvar:hover { background: #218838; }
        .msg { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; font-weight: bold; text-align: center; }
        .msg.sucesso { background: #d4edda; color: #155724; display: block; }
        .msg.erro { background: #f8d7da; color: #721c24; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Configurações do Sistema</h1>
        <p class="desc">Selecione o tipo de entidade para aplicar o limite correto de Custo de Pessoal, conforme a Resolução Cofen 814/2026.</p>
        
        <label class="opcao" id="opcao-cofen">
            <input type="radio" name="entidade" value="COFEN" onchange="selecionar('COFEN')">
            <div>
                <div class="titulo">COFEN (Conselho Federal)</div>
                <div class="sub">Limite de 50% da Receita Corrente Líquida (RCL)</div>
            </div>
        </label>
        
        <label class="opcao" id="opcao-coren">
            <input type="radio" name="entidade" value="COREN" onchange="selecionar('COREN')">
            <div>
                <div class="titulo">COREN (Conselho Regional)</div>
                <div class="sub">Limite de 60% da Receita Corrente Líquida (RCL)</div>
            </div>
        </label>
        
        <button class="btn-salvar" onclick="salvar()">Salvar Configuração</button>
        <div class="msg" id="msg"></div>
    </div>

    <script>
        var entidadeAtual = 'COFEN';

        function selecionar(ent) {
            entidadeAtual = ent;
            document.getElementById('opcao-cofen').classList.toggle('ativo', ent === 'COFEN');
            document.getElementById('opcao-coren').classList.toggle('ativo', ent === 'COREN');
        }

        function carregar() {
            fetch('/api/configuracoes')
                .then(r => r.json())
                .then(d => {
                    var ent = d.tipo_entidade || 'COFEN';
                    entidadeAtual = ent;
                    document.querySelector('input[value="' + ent + '"]').checked = true;
                    selecionar(ent);
                });
        }

        function salvar() {
            fetch('/api/configuracoes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo_entidade: entidadeAtual})
            })
            .then(r => r.json())
            .then(d => {
                var msg = document.getElementById('msg');
                msg.className = 'msg sucesso';
                msg.innerText = 'Configuração salva com sucesso! Tipo: ' + entidadeAtual;
                setTimeout(() => msg.className = 'msg', 3000);
            })
            .catch(e => {
                var msg = document.getElementById('msg');
                msg.className = 'msg erro';
                msg.innerText = 'Erro ao salvar: ' + e.message;
            });
        }

        window.onload = carregar;
    </script>
</body>
</html>'''

Path("pc_frontend/configuracoes.html").write_text(html, encoding="utf-8")
print("OK: configuracoes.html criado!")
