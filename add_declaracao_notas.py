import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_declaracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona a seção de declaração antes do fechamento do </body>
declaracao_html = """
<div id="declaracao-conformidade" style="margin-top: 40px; padding: 20px; background: #f4f7f9; border-left: 5px solid #003366; font-size: 11px; line-height: 1.6; text-align: justify; color: #333; page-break-inside: avoid;">
    <h3 style="color: #003366; margin-bottom: 15px;">Declaração de Conformidade</h3>
    <p>Declaramos, na qualidade de responsáveis pela gestão e pela elaboração das demonstrações contábeis consolidadas do Conselho Federal de Enfermagem (COFEN), referentes ao período de 01/01/2026 a 30/09/2026 (2026-TRIMESTRE-3), que:</p>
    <p>1. As informações contábeis foram elaboradas em conformidade com as disposições da Lei nº 4.320/1964, as diretrizes do Manual de Contabilidade Aplicada ao Setor Público (MCASP) e as Normas Brasileiras de Contabilidade Técnicas do Setor Público (NBC TSP).</p>
    <p>2. As demonstrações contábeis consolidadas (Balanço Patrimonial, Balanço Orçamentário, Balanço Financeiro, Demonstração das Variações Patrimoniais, Demonstração dos Fluxos de Caixa e Demonstração das Mutações do Patrimônio Líquido) refletem, de forma fidedigna, a posição patrimonial e financeira do COFEN e o desempenho da execução orçamentária no período.</p>
    <p>3. Os registros contábeis estão amparados em documentação de suporte idônea e devidamente auditada internamente, observando os princípios da legalidade, da transparência, da economicidade e da segregação de funções.</p>
    <p>4. As práticas de gestão de riscos, os controles internos administrativos e o processo de conformidade foram implementados e mantidos operantes durante todo o período analisado, garantindo a integridade dos dados apresentados.</p>
    <p>5. Esta declaração é firmada com base nas informações extraídas dos sistemas corporativos e validadas pelos responsáveis técnicos, nos termos da Resolução COFEN nº 764/2024 (Prestação de Contas).</p>
    
    <div style="margin-top: 30px; text-align: center;">
        <p style="margin: 0;"><b id="nome-contador">Marcelo Ribeiro Medeiros</b></p>
        <p style="margin: 0;">CRC: <span id="crc-contador">RJ-066005/O-8T</span></p>
        <p style="margin: 0;">CPF: <span id="cpf-contador">***.212.***-**</span></p>
    </div>
</div>
"""

if 'declaracao-conformidade' not in html:
    html = html.replace('</body>', declaracao_html + '</body>')

# Adiciona a função para carregar os dados do contador
funcao_contador = """
// Carrega os dados do contador do banco
fetch('/api/configuracoes/entidade')
    .then(r => r.json())
    .then(data => {
        if (data.contador_nome) document.getElementById('nome-contador').innerText = data.contador_nome;
        if (data.contador_crc) {
            const crc = data.contador_crc;
            const uf = data.contador_uf || '';
            const crcFormatado = crc.length === 11 ? crc.slice(0,2) + '-' + crc.slice(2,8) + '/' + crc.slice(8,9) + '-' + crc.slice(9) : crc;
            document.getElementById('crc-contador').innerText = crcFormatado;
        }
        if (data.contador_cpf) document.getElementById('cpf-contador').innerText = data.contador_cpf;
    });
"""

if 'function carregarContador' not in html:
    html = html.replace('carregarHistorico();', funcao_contador + '\ncarregarHistorico();')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Declaração de conformidade e dados do contador adicionados.")
