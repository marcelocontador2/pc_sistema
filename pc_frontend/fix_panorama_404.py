import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao carregarPanorama para tratar o 404 (que o backend retorna quando nao ha dados)
padrao = re.compile(r'async function carregarPanorama\(\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''async function carregarPanorama() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    const valor = document.getElementById('trimestre').value;
    const periodo = `${ano}-${tipo}-${valor}`;
    
    document.getElementById('periodo-titulo').innerText = `Resultados Gerais — ${valor}º Trimestre de ${ano}`;
    
    try {
        const response = await fetch(`/api/panorama/${periodo}`);
        
        // Se o backend responder 404, significa que nao ha dados para o periodo
        if (response.status === 404) {
            alert("Aviso: Não há demonstrativos importados para o período " + periodo + ". Verifique se os relatórios foram enviados.");
            preencherCards({}); // Limpa os cards
            return;
        }
        
        if (!response.ok) {
            throw new Error("Erro HTTP " + response.status);
        }
        
        const data = await response.json();
        
        if (data.erro) { 
            alert("Aviso: " + (data.mensagem || "Faltam demonstrativos importados para este período.")); 
            preencherCards({}); 
            return; 
        }
        
        // Verifica se todos os valores numericos estao zerados
        const valores = Object.values(data).filter(v => typeof v === 'number');
        const todosZerados = valores.length > 0 && valores.every(v => v === 0);
        
        if (todosZerados || valores.length === 0) {
            alert("Aviso: Não há demonstrativos importados para o período " + periodo + ". Verifique se os relatórios foram enviados.");
            preencherCards({});
            return;
        }
        
        dadosAtuais = data;
        preencherCards(data);
        
        const btnSalvar = document.getElementById("btn-salvar");
        if(btnSalvar) {
            btnSalvar.setAttribute("data-periodo", periodo);
            btnSalvar.style.display = "inline-block";
            btnSalvar.innerText = "Confirmar e Salvar";
            btnSalvar.disabled = false;
        }
    } catch (e) { 
        console.error(e); 
        alert("Erro de conexão ao buscar panorama.");
    }
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao carregarPanorama atualizada para tratar o 404 e avisar o usuario!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao carregarPanorama.")
