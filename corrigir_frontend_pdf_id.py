from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Atualizar o gerarPDF() para passar o id do historico
trecho_antigo = '''function gerarPDF() {
            var periodo = document.getElementById('periodo-select').value;
            window.open('/gerar_pdf_custo_pessoal?periodo=' + periodo, '_blank');
        }'''

trecho_novo = '''function gerarPDF() {
            var check = document.querySelector('.check-historico:checked');
            if (!check) { 
                alert('Selecione um historico antes de gerar o PDF.'); 
                return; 
            }
            window.open('/gerar_pdf_custo_pessoal?id=' + check.value, '_blank');
        }'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: gerarPDF() atualizado (passa o id do historico)!")
else:
    print("AVISO: nao achei o gerarPDF() antigo")

# 2. Atualizar o gerarPDFCompleto() para passar o id do historico
trecho_antigo2 = '''function gerarPDFCompleto() {
            var periodo = document.getElementById('periodo-select').value;
            window.open('/gerar_pdf_completo_custo_pessoal?periodo=' + periodo, '_blank');
        }'''

trecho_novo2 = '''function gerarPDFCompleto() {
            var check = document.querySelector('.check-historico:checked');
            if (!check) { 
                alert('Selecione um historico antes de gerar o PDF.'); 
                return; 
            }
            window.open('/gerar_pdf_completo_custo_pessoal?id=' + check.value, '_blank');
        }'''

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: gerarPDFCompleto() atualizado (passa o id do historico)!")
else:
    print("AVISO: nao achei o gerarPDFCompleto() antigo")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
