import re

c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

# Encontra a função verificar e substitui por uma versão com try/catch
padrao = r'async function verificar\(\) \{.*?\n        \}'
nova_func = '''async function verificar() {
            const statusDiv = document.getElementById('status') || document.createElement('div');
            const periodoAtual = `${document.getElementById('ano').value}-${document.getElementById('tipo').value}-${document.getElementById('valor').value}`;
            
            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodoAtual}?_t=${Date.now()}`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                
                console.log("[DEBUG] Dados recebidos da API:", data);
                
                if (data.erro) {
                    alert("Erro da API: " + data.mensagem);
                    document.getElementById('tabela-container').innerHTML = `<p style="padding:20px; color:red;">Erro: ${data.mensagem}</p>`;
                    return;
                }
                
                atualizarCards(data);
                renderizarTabela(data);
                document.getElementById('tabela-container').scrollIntoView({ behavior: 'smooth' });
                
            } catch (e) {
                console.error("[ERRO JS]", e);
                alert("Falha ao carregar os dados: " + e.message);
            }
        }'''
        
c = re.sub(padrao, nova_func, c, flags=re.DOTALL)
open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] Função verificar() blindada com try/catch!")
