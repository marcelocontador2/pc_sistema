import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui o bloco da função carregarPanorama para verificar se os dados estão zerados
padrao = re.compile(r'function\s+carregarPanorama\(\)\s*\{.*?(?=\n\s*(?:async\s+)?function|\Z)', re.DOTALL)

nova_funcao = '''async function carregarPanorama() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    const valor = document.getElementById('trimestre').value;
    const periodo = `${ano}-${tipo}-${valor}`;
    
    document.getElementById('periodo-titulo').innerText = `Resultados Gerais — ${valor}º Trimestre de ${ano}`;
    
    try {
        const response = await fetch(`/api/panorama/${periodo}`);
        const data = await response.json();
        
        // 1. Verifica se o backend retornou erro explicito
        if (data.erro) { 
            alert("Aviso: " + (data.mensagem || "Faltam demonstrativos importados para este período.")); 
            // Limpa os cards para nao mostrar lixo
            preencherCards({}); 
            return; 
        }
        
        // 2. Verifica se TODOS os valores estao zerados (indicando que nao ha dados)
        const valores = Object.values(data).filter(v => typeof v === 'number');
        const todosZerados = valores.length > 0 && valores.every(v => v === 0);
        
        if (todosZerados || valores.length === 0) {
            alert("Aviso: Não há demonstrativos importados para o período " + periodo + ". Verifique se os relatórios foram enviados.");
            preencherCards({});
            return;
        }
        
        dadosAtuais = data; // Guarda o JSON correto na memória
        preencherCards(data);
        
        const btnSalvar = document.getElementById("btn-salvar");
        btnSalvar.setAttribute("data-periodo", periodo);
        btnSalvar.style.display = "inline-block";
        btnSalvar.innerText = "Confirmar e Salvar";
        btnSalvar.disabled = false;
    } catch (e) { 
        console.error(e); 
        alert("Erro de conexão ao buscar panorama.");
    }
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao carregarPanorama atualizada com aviso de dados ausentes/zerados!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao carregarPanorama.")
