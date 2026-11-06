import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_financeira_bf.html"
shutil.copy2(arq, f"{arq}.bak_totais_bf_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Vamos localizar o final da função render, onde o HTML é construído
# Procuramos pela linha que fecha o innerHTML da tabela (geralmente tb.innerHTML = html;)
idx = c.find("tb.innerHTML = html;")
if idx == -1:
    print("[ERRO] Nao encontrei o 'tb.innerHTML = html;'.")
    exit(1)

# Encontra onde o HTML da tabela termina antes do innerHTML
# Vamos inserir o novo bloco de totais antes do 'tb.innerHTML = html;'
novo_bloco = '''
            // ==========================================
            // TOTAIS DE INGRESSOS E DISPÊNDIOS
            // ==========================================
            
            // Ingressos: Receitas + Extra + Saldo Anterior
            const ing_rec_at = at.receitas.total.atual || 0;
            const ing_ext_at = at.extra.recebimentos.atual || 0;
            const ing_sal_at = at.caixa.saldo_anterior.atual || 0;
            const total_ing_at = ing_rec_at + ing_ext_at + ing_sal_at;

            const ing_rec_ant = at.receitas.total.anterior || 0;
            const ing_ext_ant = at.extra.recebimentos.anterior || 0;
            const ing_sal_ant = at.caixa.saldo_anterior.anterior || 0;
            const total_ing_ant = ing_rec_ant + ing_ext_ant + ing_sal_ant;

            // Dispêndios: Despesas + Extra + Saldo Seguinte
            const disp_desp_at = at.despesas.total.atual || 0;
            const disp_ext_at = at.extra.pagamentos.atual || 0;
            const disp_sal_at = at.caixa.saldo_seguinte.atual || 0;
            const total_disp_at = disp_desp_at + disp_ext_at + disp_sal_at;

            const disp_desp_ant = at.despesas.total.anterior || 0;
            const disp_ext_ant = at.extra.pagamentos.anterior || 0;
            const disp_sal_ant = at.caixa.saldo_seguinte.anterior || 0;
            const total_disp_ant = disp_desp_ant + disp_ext_ant + disp_sal_ant;

            // Renderiza o Bloco de Ingressos
            html += '<tr><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#0056b3; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE INGRESSOS</td></tr>';
            
            const line_ing = (label, va, vb) => `<tr><td>${label}</td><td style="text-align:right;">${fmtV(va)}</td><td style="text-align:right;">${fmtV(vb)}</td><td style="text-align:right;">-</td></tr>`;
            
            html += line_ing('Receitas Orçamentárias (Corrente + Capital)', ing_rec_at, ing_rec_ant);
            html += line_ing('Recebimentos Extraorçamentários', ing_ext_at, ing_ext_ant);
            html += line_ing('Saldo em Espécie do Exercício Anterior', ing_sal_at, ing_sal_ant);
            
            html += `<tr style="font-weight:bold; background:#e9ecef; color:#0056b3;">
                <td>TOTAL DE INGRESSOS</td>
                <td style="text-align:right;">${fmtV(total_ing_at)}</td>
                <td style="text-align:right;">${fmtV(total_ing_ant)}</td>
                <td style="text-align:right;">-</td>
            </tr>`;

            // Renderiza o Bloco de Dispêndios
            html += '<tr><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#dc3545; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE DISPÊNDIOS</td></tr>';
            
            html += line_ing('Despesa Orçamentária (Corrente + Capital)', disp_desp_at, disp_desp_ant);
            html += line_ing('Pagamentos Extraorçamentários', disp_ext_at, disp_ext_ant);
            html += line_ing('Saldo em Espécie para o Exercício Seguinte', disp_sal_at, disp_sal_ant);

            html += `<tr style="font-weight:bold; background:#e9ecef; color:#dc3545;">
                <td>TOTAL DE DISPÊNDIOS</td>
                <td style="text-align:right;">${fmtV(total_disp_at)}</td>
                <td style="text-align:right;">${fmtV(total_disp_ant)}</td>
                <td style="text-align:right;">-</td>
            </tr>`;
'''

# Insere o bloco logo antes de 'tb.innerHTML = html;'
c = c[:idx] + novo_bloco + "\n            " + c[idx:]

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Blocos de Ingressos e Dispêndios adicionados ao Balanço Financeiro.")
