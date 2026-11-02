c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Adicionar o botão na toolbar
if "Importar CSV" not in c:
    c = c.replace(
        '<button class="btn btn-verificar" onclick="verificarAnalise()">Verificar Análise</button>',
        '<button class="btn btn-importar" onclick="document.getElementById(''file-csv'').click()" style="background-color: #6f42c1; color: white;">Importar CSV</button>\n            <input type="file" id="file-csv" accept=".csv" style="display: none;" onchange="importarCSV(event)">\n            <button class="btn btn-verificar" onclick="verificarAnalise()">Verificar Análise</button>'
    )

# 2. Adicionar a função importarCSV no JavaScript
if "function importarCSV" not in c:
    funcao_js = """
        async function importarCSV(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const r = await fetch('/api/centro_custos/importar', {
                    method: 'POST',
                    body: formData
                });
                const d = await r.json();
                
                if (d.erro) {
                    alert('Erro ao importar: ' + d.mensagem);
                    return;
                }
                
                if (d.centros && d.centros.length > 0) {
                    dadosAtuais = d;
                    renderizarTabela(d);
                    alert('CSV importado com sucesso! ' + d.centros.length + ' centros encontrados. Clique em "Confirmar e Salvar" para gravar.');
                } else {
                    alert('Nenhum dado encontrado no CSV.');
                }
            } catch (e) {
                console.error(e);
                alert('Erro ao importar o arquivo.');
            }
            
            // Limpa o input para permitir importar o mesmo arquivo novamente
            event.target.value = '';
        }
    """
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + funcao_js + "\n" + c[pos:]
        print("[OK] Função importarCSV adicionada!")

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão e lógica de importação CSV adicionados!")
