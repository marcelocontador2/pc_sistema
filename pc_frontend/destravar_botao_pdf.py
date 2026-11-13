import re

arquivo = 'analise_comparativo_despesas.html'
c = open(arquivo, encoding='utf-8').read()

# 1. Garante que o botão chama a função correta (caso não tenha mudado antes)
c = c.replace('onclick="window.print()"', 'onclick="gerarPDF()"')

# 2. Limpa qualquer versão quebrada da função gerarPDF que possa ter sido injetada errado
c = re.sub(r'function gerarPDF\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)

# 3. Cria a função perfeita e limpa
funcao_nova = """
        function gerarPDF() {
            console.log("Botão de PDF clicado! Verificando histórico...");
            const sel = document.querySelector('input[name="historico"]:checked');
            
            if (!sel) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            
            const url = `/gerar_pdf_comparativo_despesas?historico_id=${sel.value}`;
            console.log("Abrindo PDF:", url);
            window.open(url, '_blank');
        }
"""

# 4. Injeta a função exatamente antes do fechamento da tag </script>
if '</script>' in c:
    c = c.replace('</script>', funcao_nova + '\n    </script>')
    open(arquivo, 'w', encoding='utf-8').write(c)
    print("[OK] Função gerarPDF injetada com sucesso e botão destravado!")
else:
    print("[ERRO] Tag </script> não encontrada no arquivo.")
