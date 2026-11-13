import re
import shutil

# O arquivo do HTML do PDF do panorama (pode ter outro nome, vamos procurar)
import os
arquivos = [f for f in os.listdir('.') if 'panorama' in f.lower() and f.endswith('.html')]
print(f"Arquivos encontrados: {arquivos}")

if not arquivos:
    print("ERRO: Nenhum arquivo HTML de panorama encontrado.")
else:
    path = arquivos[0]  # Pega o primeiro
    print(f"Usando o arquivo: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    
    shutil.copy(path, path + ".bak_pdf_formal")
    
    # Substitui o CSS e a estrutura para ficar formal
    novo_css = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body { 
        font-family: 'Roboto', Arial, sans-serif; 
        color: #333; 
        padding: 30px 40px;
        font-size: 10pt;
        background: #fff;
    }
    
    .header {
        text-align: center;
        border-bottom: 2px solid #002244;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    .header h1 { font-size: 14pt; color: #002244; text-transform: uppercase; letter-spacing: 1px; }
    .header h2 { font-size: 11pt; color: #555; font-weight: normal; margin-top: 5px; }
    
    .info { display: flex; justify-content: space-between; font-size: 9pt; color: #666; margin-bottom: 20px; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #ccc; padding: 8px 10px; text-align: left; }
    th { background: #f0f4f8; color: #002244; font-weight: bold; text-transform: uppercase; font-size: 9pt; }
    td.valor { text-align: right; font-weight: bold; }
    
    .footer { margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 8pt; color: #999; text-align: center; }
    
    .neg { color: #c0392b; }
    .pos { color: #27ae60; }
</style>
'''
    
    # Remove o CSS antigo e injeta o novo
    s = re.sub(r'<style>.*?</style>', novo_css, s, flags=re.DOTALL | re.IGNORECASE)
    
    # Substitui a estrutura dos cards por uma tabela formal
    novo_html = '''
<div class="header">
    <h1>Relatório Executivo - Panorama de Resultados</h1>
    <h2>COFEN - Conselho Federal de Enfermagem</h2>
</div>

<div class="info">
    <span><strong>Período:</strong> {{periodo}}</span>
    <span><strong>Emissão:</strong> {{data}}</span>
</div>

<table>
    <thead>
        <tr>
            <th>Indicador</th>
            <th style="text-align: right;">Valor (R$)</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Caixa e Equivalente (BP)</td><td class="valor">{{caixa}}</td></tr>
        <tr><td>Ativo Total (BP)</td><td class="valor">{{ativo}}</td></tr>
        <tr><td>Passivo Total (BP)</td><td class="valor">{{passivo}}</td></tr>
        <tr><td>Patrimônio Líquido (BP)</td><td class="valor">{{pl}}</td></tr>
        <tr><td>Receitas Realizadas (BO)</td><td class="valor pos">{{receitas}}</td></tr>
        <tr><td>Despesas Empenhadas (BO)</td><td class="valor neg">{{despesas}}</td></tr>
        <tr><td>Superávit/Déficit Orçamentário</td><td class="valor {{cls_orc}}">{{superavit_orc}}</td></tr>
        <tr><td>Superávit Patrimonial (DVP)</td><td class="valor {{cls_pat}}">{{superavit_pat}}</td></tr>
        <tr><td>Superávit Financeiro (BP)</td><td class="valor {{cls_fin}}">{{superavit_fin}}</td></tr>
    </tbody>
</table>

<div class="footer">
    SGPC - Sistema de Gestão de Prestação de Contas | Documento Confidencial - Uso Exclusivo da Diretoria
</div>
'''
    
    # Aqui você pode substituir a div "cards-grid" pelo novo HTML
    # Como o PDF é gerado via Playwright, podemos simplesmente trocar o conteúdo do body
    s = re.sub(r'<body>.*?</body>', f'<body>{novo_html}</body>', s, flags=re.DOTALL | re.IGNORECASE)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    print("OK: Layout do PDF substituído por um modelo formal e executivo!")
