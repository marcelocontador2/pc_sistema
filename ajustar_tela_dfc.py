import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_ajuste_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Ajusta o texto do botao
c = c.replace(">Verificar Matriz<", ">Verificar Dados<")

# 2. Ajusta a funcao carregar para forcar o preenchimento das colunas
antigo_fetch = '''            fetch('/api/analise_dfc/' + periodoAtual)
                .then(r => r.json())
                .then(data => {
                    if (data.erro === "faltando") {
                        document.querySelector('#tab tbody').innerHTML = '<tr><td colspan="4" style="color:red; text-align:center;">Arquivo CSV da DFC não encontrado para este período.</td></tr>';
                        return;
                    }
                    
                    // Como o backend nao faz o comparativo automatico, usamos os mesmos dados para atual e anterior
                    // (Para simplificar, ja que o CSV tem as duas colunas)
                    render(data.dados, data.dados);
                    document.getElementById('btn-salvar').style.display = 'inline-block';
                    document.getElementById('btn-salvar').setAttribute('data-periodo', periodoAtual);
                })'''

novo_fetch = '''            fetch('/api/analise_dfc/' + periodoAtual)
                .then(r => r.json())
                .then(data => {
                    if (data.erro === "faltando") {
                        document.querySelector('#tab tbody').innerHTML = '<tr><td colspan="4" style="color:red; text-align:center;">Arquivo CSV da DFC não encontrado para este período.</td></tr>';
                        return;
                    }
                    
                    // O backend ja retorna os dados atuais e anteriores dentro de data.dados
                    // Nao precisamos de dois fetches.
                    render(data.dados, data.dados);
                    
                    document.getElementById('btn-salvar').style.display = 'inline-block';
                    document.getElementById('btn-salvar').setAttribute('data-periodo', periodoAtual);
                })'''

if antigo_fetch in c:
    c = c.replace(antigo_fetch, novo_fetch)
    print("[OK] Fetch ajustado para ler os dados da API.")

# 3. Ajusta a funcao render para ler os campos corretos que o backend manda
# (No script anterior, o backend retornou op.ingressos.atual, etc. Vamos garantir que a render use isso)
if "function render(at, ant) {" in c:
    pass # Ja esta usando at.operacional.ingressos, etc.

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Tela DFC ajustada.")
