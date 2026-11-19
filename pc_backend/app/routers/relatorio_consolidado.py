from pc_backend.app.db_memoria import carregar_contas_memoria
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import psycopg2

from pc_backend.app.config import PG_CONFIG


def fmt_sem_rs(v):
    if v is None: return "-"
    if isinstance(v, (int, float)):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v).replace("R$", "").strip()

router = APIRouter(tags=["relatorio_consolidado"])


def _get_conn():
    return psycopg2.connect(**PG_CONFIG)


@router.get("/relatorio_consolidado")
async def serve_relatorio_consolidado():
    import os
    from fastapi.responses import FileResponse
    caminho = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pc_frontend", "relatorio_consolidado.html")
    )
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})


@router.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    modulos = {
        "analise_bp": "historico_analise_bp",
        "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial",
        "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf",
        "comparativo_receitas": "historico_comparativo_receitas",
        "comparativo_despesas": "historico_comparativo_despesas",
        "panorama": "historico_panorama",
        "liquidez": "historico_liquidez",
        "integridade": "historico_integridade_matriz",
        "conferencia": "historico_conferencia",
        "custo_pessoal": "historico_custo_pessoal",
        "centro_custos": "historico_centro_custos",
        "dmpl": "historico_analise_dmpl",
    }

    nomes_amigaveis = {
        "analise_bp": "An?lise BP",
        "analise_dfc": "An?lise DFC",
        "analise_patrimonial": "An?lise Patrimonial (DVP)",
        "analise_orcamentaria": "An?lise Or?ament?ria (BO)",
        "analise_financeira_bf": "An?lise Financeira (BF)",
        "comparativo_receitas": "Comparativo de Receitas",
        "comparativo_despesas": "Comparativo de Despesas",
        "panorama": "Panorama de Resultados",
        "liquidez": "Índices de Liquidez",
        "integridade": "Integridade entre Demonstra??es",
        "conferencia": "Confer?ncia das Demonstra??es",
        "custo_pessoal": "Custo de Pessoal",
        "centro_custos": "An?lise por Centro de Custos",
        "dmpl": "Demonstra??o das Muta??es do PL (DMPL)",
    }

    encontrados = []
    faltando = []

    try:
        conn = _get_conn()
        cursor = conn.cursor()

        for chave, tabela in modulos.items():
            try:
                if chave in ("analise_financeira_bf", "dmpl", "analise_bp", "analise_dfc", "analise_dvp"):
                    cursor.execute(
                        f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1",
                        (f"%{periodo}%",),
                    )
                else:
                    cursor.execute(
                        f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s ORDER BY id DESC LIMIT 1",
                        (periodo,),
                    )
                row = cursor.fetchone()
                if row:
                    encontrados.append({
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 and row[1] else "Dispon?vel",
                        "id": row[0],
                    })
                else:
                    faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
            except Exception:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})

        cursor.close()
        conn.close()

        status = "ok" if len(faltando) == 0 else "faltando"
        return {
            "status": status,
            "encontrados": encontrados,
            "faltando": faltando,
            "periodo": periodo,
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro de conex?o com o PostgreSQL: {str(e)}",
        }


@router.post("/salvar_relatorio_consolidado/{periodo}")
async def salvar_relatorio_consolidado_novo(periodo: str):
    try:
        dados_api = await api_relatorio_consolidado_novo(periodo)
        if dados_api.get("status") == "erro":
            return {"ok": False, "mensagem": dados_api.get("mensagem", "Erro ao consultar m?dulos no PostgreSQL.")}

        if dados_api.get("status") == "faltando" and len(dados_api.get("faltando", [])) > 0:
            return {
                "ok": False,
                "mensagem": f"Faltam {len(dados_api['faltando'])} m?dulo(s) para consolidar.",
                "faltando": dados_api["faltando"],
            }

        dados_consolidados = {
            "periodo": periodo,
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "dados": dados_api.get("encontrados", []),
        }
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (periodo, data_agora, json.dumps(dados_consolidados, ensure_ascii=False)),
        )
        novo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "ok": True,
            "id": novo_id,
            "mensagem": "Relat?rio salvo com sucesso no PostgreSQL!",
        }
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico_relatorio_consolidado")
async def get_hist_consolidado():
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {
                "id": r[0],
                "periodo": r[1],
                "data_geracao": r[2],
                "dados": r[3] if len(r) > 3 and r[3] else "{}",
            }
            for r in rows
        ]
    except Exception:
        return []


@router.get("/historico_relatorio_consolidado/{id}")
async def get_historico_consolidado(id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s",
        (id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {"erro": "Hist?rico n?o encontrado"}

    dados_obj = row[2]
    if isinstance(dados_obj, str):
        try:
            dados_obj = json.loads(dados_obj)
        except Exception:
            pass

    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": dados_obj,
    }


@router.delete("/excluir_relatorio_consolidado/{id}")
async def excluir_relatorio_consolidado(id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_relatorio_consolidado WHERE id = %s", (id,))
    removidos = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return {"ok": removidos > 0, "removidos": removidos}


@router.post("/excluir_multiplos_relatorio_consolidado")
async def excluir_multiplos_relatorio_consolidado(request: Request):
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids:
            return {"ok": False, "mensagem": "Nenhum ID v?lido informado."}
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM historico_relatorio_consolidado WHERE id = ANY(%s)",
            (ids,),
        )
        removidos = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "removidos": removidos}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/api/observacoes_consolidado/{relatorio_id}")
async def get_observacoes(relatorio_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, relatorio_id, item, texto, data_criacao, ano, periodo
        FROM observacoes_consolidado
        WHERE relatorio_id = %s
        ORDER BY id ASC
        """,
        (relatorio_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "relatorio_id": r[1],
            "item": r[2],
            "texto": r[3],
            "data_criacao": r[4],
            "ano": r[5],
            "periodo": r[6],
        }
        for r in rows
    ]


@router.post("/api/observacoes_consolidado/{relatorio_id}")
async def post_observacao(relatorio_id: int, request: Request):
    dados = await request.json()
    item = str(dados.get("item", "")).strip()
    texto = str(dados.get("texto", "")).strip()
    ano = dados.get("ano")
    periodo = dados.get("periodo")
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO observacoes_consolidado (relatorio_id, item, texto, data_criacao, ano, periodo)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (relatorio_id, item, texto, agora, ano, periodo),
    )
    novo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"ok": True, "id": novo_id, "data_criacao": agora}


@router.put("/api/observacoes_consolidado/{obs_id}")
async def put_observacao(obs_id: int, request: Request):
    dados = await request.json()
    item = str(dados.get("item", "")).strip()
    texto = str(dados.get("texto", "")).strip()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE observacoes_consolidado
        SET item = COALESCE(NULLIF(%s, ''), item),
            texto = %s,
            data_criacao = %s
        WHERE id = %s
        """,
        (item, texto, agora, obs_id),
    )
    atualizados = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return {"ok": atualizados > 0, "atualizados": atualizados}


@router.delete("/api/observacoes_consolidado/{obs_id}")
async def del_observacao(obs_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM observacoes_consolidado WHERE id = %s", (obs_id,))
    removidos = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return {"ok": removidos > 0, "removidos": removidos}


@router.get("/api/conclusao_consolidado/{relatorio_id}")
async def get_conclusao(relatorio_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, relatorio_id, texto, data_criacao
        FROM conclusao_consolidado
        WHERE relatorio_id = %s
        ORDER BY id DESC LIMIT 1
        """,
        (relatorio_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return {"relatorio_id": relatorio_id, "texto": "", "data_criacao": None}
    return {"id": row[0], "relatorio_id": row[1], "texto": row[2], "data_criacao": row[3]}


@router.post("/api/conclusao_consolidado/{relatorio_id}")
async def post_conclusao(relatorio_id: int, request: Request):
    dados = await request.json()
    texto = str(dados.get("texto", "")).strip()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM conclusao_consolidado WHERE relatorio_id = %s ORDER BY id DESC LIMIT 1", (relatorio_id,))
    existente = cursor.fetchone()
    if existente:
        cursor.execute(
            "UPDATE conclusao_consolidado SET texto = %s, data_criacao = %s WHERE id = %s",
            (texto, agora, existente[0]),
        )
        reg_id = existente[0]
    else:
        cursor.execute(
            "INSERT INTO conclusao_consolidado (relatorio_id, texto, data_criacao) VALUES (%s, %s, %s) RETURNING id",
            (relatorio_id, texto, agora),
        )
        reg_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"ok": True, "id": reg_id, "data_criacao": agora}


@router.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from fastapi.responses import Response
    import json
    from playwright.sync_api import sync_playwright
    import os
    import base64
    import traceback

    def fmt(v):
        if v is None: return "-"
        if isinstance(v, (int, float)):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(v)
    
    def pct(v):
        if v is None: return "-"
        return f"{v:+.2f}%".replace(".", ",")
    
    def calc_var(atual, anterior):
        if anterior and anterior != 0:
            return ((atual - anterior) / abs(anterior)) * 100
        return 0.0
    
    mapa_tabelas = {
        "Integridade entre Demonstrações": ("historico_integridade_matriz", "resultado_json"),
        "Análise BP": ("historico_analise_bp", "resultado_json"),
        "Análise Orçamentária (BO)": ("historico_analise_orcamentaria", "resultado_json"),
        "Análise Financeira (BF)": ("historico_analise_financeira_bf", "resultado_json"),
        "Análise DFC": ("historico_analise_dfc", "resultado_json"),
        "Análise Patrimonial (DVP)": ("historico_analise_patrimonial", "resultado_json"),
        "DMPL": ("historico_analise_dmpl", "resultado_json"),
        "Demonstração das Mutações do PL (DMPL)": ("historico_analise_dmpl", "resultado_json"),
        "Comparativo de Receitas": ("historico_comparativo_receitas", "dados_json"),
        "Comparativo de Despesas": ("historico_comparativo_despesas", "dados_json"),
        "Índices de Liquidez": ("historico_liquidez", "resultado_json"),
        "Panorama de Resultados": ("historico_panorama", "resultado_json"),
        "Análise por Centro de Custos": ("historico_centro_custos", "dados_json"),
        "Custo de Pessoal": ("historico_custo_pessoal", "resultado_json"),
        "Conferência das Demonstrações": ("historico_conferencia", "resultado_json")
    }
    
    ordem_modelo = [
        ("Conferência das Demonstrações", "1. Conferência das Demonstrações"),
        ("Integridade entre Demonstrações", "2. Integridade entre Demonstrações"),
        ("Análise BP", "3. Análise do Balanço Patrimonial"),
        ("Análise Orçamentária (BO)", "4. Análise do Balanço Orçamentário"),
        ("Análise Financeira (BF)", "5. Análise do Balanço Financeiro"),
        ("Análise DFC", "6. Análise do Fluxo de Caixa"),
        ("Análise Patrimonial (DVP)", "7. Análise das Variações Patrimoniais"),
        ("Demonstração das Mutações do PL (DMPL)", "8. Demonstração das Mutações do Patrimônio LÍ­quido (DMPL)"),
        ("Comparativo de Receitas", "9. Comparativo de Receitas"),
        ("Comparativo de Despesas", "10. Comparativo de Despesas"),
        ("Índices de Liquidez", "11. Índices de Liquidez e Estrutura"),
        ("Panorama de Resultados", "12. Panorama de Resultados"),
        ("Análise por Centro de Custos", "13. Análise por Centro de Custos"),
        ("Custo de Pessoal", "14. Custo de Pessoal"),
    ]
    
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        
        # 1. Busca dados da entidade COFEN (fixo)
        cursor.execute("SELECT logo_path FROM configuracoes_entidade WHERE razao_social ILIKE '%COFEN%' OR razao_social ILIKE '%Conselho Federal%' ORDER BY id DESC LIMIT 1")
        ent_row = cursor.fetchone()
        logo_path = ent_row[0] if ent_row else ""
        
        # Dados fixos do COFEN
        razao_social = "COFEN - Conselho Federal de Enfermagem"
        cnpj = "47.217.146/0001-57"
        contador_nome = "Marcelo Ribeiro Medeiros"
        contador_crc = "066005O8T"
        contador_uf = "DF"
        contador_cpf = "***.212.***.***"
        
        # Converte logo para base64 (se existir)
        logo_base64 = ""
        if logo_path:
            caminho_logo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pc_storage", "uploads_logos", logo_path))
            if os.path.exists(caminho_logo):
                with open(caminho_logo, "rb") as img:
                    logo_base64 = base64.b64encode(img.read()).decode("utf-8")
        
        # 2. Busca dados do relatório consolidado
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (id,))
        row = cursor.fetchone()
        if not row:
            return Response(content="Relatório não encontrado.", status_code=404, media_type="text/plain")
        
        periodo, data_geracao, res_json = row
        dados_consolidados = json.loads(res_json)
        import re
        import unicodedata
        def _norm_key(s):
            s = str(s or "").strip().lower().replace("?", " ")
            s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
            return re.sub(r"[^a-z0-9]+", " ", s).strip()

        modulos_lista = dados_consolidados.get("dados", [])
        modulos_por_nome = {m.get("nome"): m for m in modulos_lista}
        modulos_por_norm = {_norm_key(m.get("nome")): m for m in modulos_lista if m.get("nome")}

        def _buscar_modulo(nome_chave):
            if nome_chave in modulos_por_nome:
                return modulos_por_nome[nome_chave]
            nk = _norm_key(nome_chave)
            if nk in modulos_por_norm:
                return modulos_por_norm[nk]
            # Correspondencia parcial por palavras-chave principais
            for k_norm, mod_obj in modulos_por_norm.items():
                if nk and (nk in k_norm or k_norm in nk):
                    return mod_obj
            return None
        
        html_parts = []
        
        # ============================================================
        # CAPA (com logo, nome da entidade e CNPJ)
        # ============================================================
        html_parts.append("<!DOCTYPE html><html><head><meta charset='UTF-8'>")
        html_parts.append("<style>")
        html_parts.append("@page { size: A4; margin: 2cm; }")
        html_parts.append("body { font-family: SegoeUI, Arial, sans-serif; font-size: 10pt; color: #333; }")
        html_parts.append("h1 { color: #003366; font-size: 22pt; text-align: center; margin-top: 20px; }")
        html_parts.append("h2 { color: #003366; font-size: 12.5pt; border-bottom: 2px solid #004b8d; padding-bottom: 5px; margin-top: 25px; }")
        html_parts.append("h3 { color: #0056b3; font-size: 7.6pt; margin-top: 15px; }")
        html_parts.append(".capa { text-align: center; padding-top: 20px; }")
        html_parts.append(".capa .logo { width: 120px; margin-bottom: 20px; }")
        html_parts.append(".capa .periodo { font-size: 12pt; color: #666; font-style: italic; margin-top: 20px; }")
        html_parts.append(".capa .orgao { font-size: 14pt; color: #003366; margin-top: 20px; }")
        html_parts.append(".capa .cnpj { font-size: 11pt; color: #666; margin-top: 5px; }")
        html_parts.append(".capa .legislacao { font-size: 8pt; color: #666; margin-top: 30px; padding: 0 40px; text-align: justify; }")
        html_parts.append(".page-break { page-break-before: always; }")
        html_parts.append("table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 9pt; }")
        html_parts.append("th { background-color: #004b8d; color: white; padding: 5px; text-align: center; border: 1px solid #ccc; font-size: 5.5pt; }")
        html_parts.append("td { padding: 4px 6px; border: 1px solid #ccc; font-size: 5.9pt; }")
        html_parts.append("tr:nth-child(even) { background-color: #f9f9f9; }")
        html_parts.append(".text-right { text-align: right; }")
        html_parts.append(".text-center { text-align: center; }")
        html_parts.append(".alerta-info { background-color: #e7f1ff; border: 1px solid #b6d4fe; padding: 10px; border-radius: 5px; margin: 15px 0; font-size: 8pt; }")
        html_parts.append(".parecer p { text-align: justify; margin-bottom: 10px; font-size: 7.6pt; }")
        html_parts.append(".parecer h3 { font-size: 7.6pt; }")
        html_parts.append(".assinatura { margin-top: 50px; text-align: center; font-size: 7.6pt; }")
        html_parts.append(".assinatura .linha { border-top: 1px solid #000; width: 300px; margin: 0 auto; }")
        html_parts.append(".grafico { width: 100%; max-width: 500px; margin: 20px auto; }")
        html_parts.append(".texto-dinamico { text-align: justify; margin: 10px 0; line-height: 1.5; font-size: 7.6pt; color: #0d47a1; }")
        html_parts.append("</style>")
        html_parts.append("<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>")
        html_parts.append("</head><body>")
        
        # --- CAPA ---
        html_parts.append("<div class='capa'>")
        if logo_base64:
            html_parts.append(f"<img class='logo' src='data:image/png;base64,{logo_base64}' alt='Logo'>")
        html_parts.append("<h1>RELATÓRIO CONSOLIDADO</h1>")
        html_parts.append("<h2 style='border: none;'>Análise Contábil</h2>")
        html_parts.append(f"<div class='orgao'>{razao_social}</div>")
        html_parts.append(f"<div class='cnpj'>CNPJ: {cnpj}</div>")
        html_parts.append(f"<div class='periodo'>PERÍODO DE ANÍLISE: {periodo}</div>")
        
        html_parts.append("<div class='legislacao'>")
        html_parts.append("<strong>LEGISLAÇÃO E NORMAS APLICADAS:</strong><br>")
        html_parts.append("Lei nº 4.320/1964 (Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços.) • ")
        html_parts.append("Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil) • ")
        html_parts.append("Normas Brasileiras de Contabilidade – Setor Público (NBC TSP) • ")
        html_parts.append("Resolução COFEN nº 764/2024 (Prestação de Contas) • ")
        html_parts.append("Resolução Cofen nº 799/2025 (Gestão de riscos e controles internos) • ")
        html_parts.append("Resolução Cofen nº 814/2026 (Limites de despesa com pessoal) • ")
        html_parts.append("Manual de Contabilidade Aplicada ao Setor Público (MCASP)")
        html_parts.append("</div>")
        
        html_parts.append("<div class='legislacao' style='margin-top: 20px;'>")
        html_parts.append("<strong>DEMONSTRAÇÕES ANALISADAS:</strong><br>")
        html_parts.append("Balancete de Verificação • Balanço Financeiro (BF) • Balanço Orçamentário (BO) • Balanço Patrimonial (BP) • Demonstração do Fluxo de Caixa (DFC) • Demonstração das Mutações do PL (DMPL) • Demonstração das Variações Patrimoniais (DVP)")
        html_parts.append("</div>")
        html_parts.append("</div>")
        
        # ============================================================
        # MÓDULOS
        # ============================================================
        for nome_interno, titulo_exibicao in ordem_modelo:
            m = _buscar_modulo(nome_interno)
            if not m and "DMPL" in nome_interno:
                m = _buscar_modulo("DMPL") or _buscar_modulo("Mutacoes do PL")
                if not m:
                    m = {"nome": "DMPL", "data_geracao": "N/A"}
            if not m:
                html_parts.append("<div class='page-break'></div>")
                html_parts.append(f"<h2>{titulo_exibicao}</h2>")
                html_parts.append("<p style='color:red;'>Módulo não encontrado nos dados consolidados.</p>")
                continue
            
            data_mod = m.get("data_geracao", "N/A")
            
            html_parts.append("<div class='page-break'></div>")
            html_parts.append(f"<h2>{titulo_exibicao}</h2>")
            html_parts.append(f"<p style='color:#666; font-style:italic; font-size: 6.2pt;'>Gerado em: {data_mod}</p>")
            
            # --- BUSCA INTELIGENTE NO MAPA_TABELAS ---
            tabela, coluna = mapa_tabelas.get(nome_interno, (None, None))
            if not tabela and "DMPL" in nome_interno:
                tabela, coluna = "historico_analise_dmpl", "resultado_json"
            # ----------------------------------------
            if not tabela:
                html_parts.append("<p style='color:red;'>Módulo sem mapeamento.</p>")
                continue
            
            try:
                cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
                mod_row = cursor.fetchone()
                
                if not mod_row or not mod_row[0]:
                    html_parts.append("<p style='color:red;'>Dados não encontrados no banco para este perÍ­odo.</p>")
                    continue
                
                mod_dados = json.loads(mod_row[0])
                
                # 1. INTEGRIDADE
                if nome_interno == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Matriz de integridade com o cruzamento de todas as demonstrações.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF.</th></tr></thead><tbody>")
                    for mi in matriz:
                        item = mi.get('item', '')
                        balancete = str(mi.get('balancete', '')).replace('R$', '').strip()
                        bp = str(mi.get('bp', '')).replace('R$', '').strip()
                        bf = str(mi.get('bf', '')).replace('R$', '').strip()
                        bo = str(mi.get('bo', '')).replace('R$', '').strip()
                        dfc = str(mi.get('dfc', '')).replace('R$', '').strip()
                        dvp = str(mi.get('dvp', '')).replace('R$', '').strip()
                        dmpl = str(mi.get('dmpl', '')).replace('R$', '').strip()
                        conf = mi.get('conf', 'OK')
                        
                        # Define a cor com base no status
                        if conf == "OK":
                            cor_conf = "#006400"  # Verde
                        elif conf.startswith("(") or conf.startswith("(("):
                            cor_conf = "#cc0000"  # Vermelho
                        else:
                            cor_conf = "#333333"  # Padrão
                        
                        html_parts.append(f"<tr><td>{item}</td><td class='text-right'>{balancete}</td><td class='text-right'>{bp}</td><td class='text-right'>{bf}</td><td class='text-right'>{bo}</td><td class='text-right'>{dfc}</td><td class='text-right'>{dvp}</td><td class='text-right'>{dmpl}</td><td class='text-center' style='color: {cor_conf}; font-weight: bold;'>{conf}</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<div class='alerta-info'>1. Os itens de conformidade em vermelho, de 1 a 4, são por estornos de restos a pagar.<br>2. Incorporação de Ativos: SOMA = 16.271.957,08.</div>")
                
                elif nome_interno == "Análise BP":
                    
                    dados_bp = mod_dados.get("dados", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo das contas do Balanço Patrimonial (perÍ­odo atual x anterior).</p>")
                    html_parts.append("<table><thead><tr><th>CONTA</th><th>PERÍODO ATUAL (R$)</th><th>PERÍODO ANTERIOR (R$)</th><th>VAR. (%)</th></tr></thead><tbody>")
                    textos = []
                    for k, v in dados_bp.items():
                        if isinstance(v, dict) and k.lower() != 'estoques':
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = calc_var(atual, anterior)
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt_sem_rs(atual)}</td><td class='text-right'>{fmt_sem_rs(anterior)}</td><td class='text-right'>{pct(var)}</td></tr>")
                            if abs(var) > 0.01:
                                direcao = "positiva" if var > 0 else "negativa"
                                textos.append(f"<li>{k.replace('_', ' ').title()}, variação {direcao} de {pct(var)}.</li>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos[:6]) + "</ul>")
                    labels = [k.replace('_', ' ').title() for k, v in dados_bp.items() if isinstance(v, dict)]
                    atual_vals = [v.get('atual', 0) for v in dados_bp.values() if isinstance(v, dict)]
                    ant_vals = [v.get('anterior', 0) for v in dados_bp.values() if isinstance(v, dict)]
                    html_parts.append("<div class='grafico'><canvas id='chartBP'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartBP'), {")
                    html_parts.append("type: 'bar',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                    html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                    html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                    html_parts.append("] },")
                    html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                    html_parts.append("});")
                    html_parts.append("</script>")
                
                # 3. ANÍLISE ORÇAMENTÍRIA (BO)
                elif nome_interno == "Análise Orçamentária (BO)":
                    
                    atual = mod_dados.get("atual", {})
                    anterior = mod_dados.get("anterior", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo das receitas e despesas orçamentárias.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>PERÍODO ATUAL</th><th>PERÍODO ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt_sem_rs(atual.get('receita_realizada'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('receita_realizada'))}</td><td class='text-right'>{pct(calc_var(atual.get('receita_realizada',0), anterior.get('receita_realizada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Empenhada</td><td class='text-right'>{fmt_sem_rs(atual.get('despesa_empenhada'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('despesa_empenhada'))}</td><td class='text-right'>{pct(calc_var(atual.get('despesa_empenhada',0), anterior.get('despesa_empenhada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Superávit/Déficit</td><td class='text-right'>{fmt_sem_rs(atual.get('superavit'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('superavit'))}</td><td class='text-right'>{pct(calc_var(atual.get('superavit',0), anterior.get('superavit',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Restos a Pagar</td><td class='text-right'>{fmt_sem_rs(atual.get('restos_pagar'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('restos_pagar'))}</td><td class='text-right'>{pct(calc_var(atual.get('restos_pagar',0), anterior.get('restos_pagar',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Receita Orçada</td><td class='text-right'>{fmt_sem_rs(atual.get('receita_orcada'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('receita_orcada'))}</td><td class='text-right'>{pct(calc_var(atual.get('receita_orcada',0), anterior.get('receita_orcada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Orçada</td><td class='text-right'>{fmt_sem_rs(atual.get('despesa_orcada'))}</td><td class='text-right'>{fmt_sem_rs(anterior.get('despesa_orcada'))}</td><td class='text-right'>{pct(calc_var(atual.get('despesa_orcada',0), anterior.get('despesa_orcada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>% Realização Receitas</td><td class='text-right'>{atual.get('pct_receita', 0):.2f}%</td><td class='text-right'>{anterior.get('pct_receita', 0):.2f}%</td><td class='text-right'>-</td></tr>")
                    html_parts.append(f"<tr><td>% Realização Despesas</td><td class='text-right'>{atual.get('pct_despesa', 0):.2f}%</td><td class='text-right'>{anterior.get('pct_despesa', 0):.2f}%</td><td class='text-right'>-</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # Textos dinâmicos (Evolução das Principais Contas)
                    textos = []
                    indicadores = [
                        ("Receita Realizada", atual.get('receita_realizada', 0), anterior.get('receita_realizada', 0)),
                        ("Despesa Empenhada", atual.get('despesa_empenhada', 0), anterior.get('despesa_empenhada', 0)),
                        ("Superávit/Déficit", atual.get('superavit', 0), anterior.get('superavit', 0)),
                        ("Restos a Pagar", atual.get('restos_pagar', 0), anterior.get('restos_pagar', 0)),
                        ("Receita Orçada", atual.get('receita_orcada', 0), anterior.get('receita_orcada', 0)),
                        ("Despesa Orçada", atual.get('despesa_orcada', 0), anterior.get('despesa_orcada', 0)),
                    ]
                    for nome_ind, v_atual, v_ant in indicadores:
                        var = calc_var(v_atual, v_ant)
                        if abs(var) > 0.01:
                            direcao = "positiva" if var > 0 else "negativa"
                            textos.append(f"<li>{nome_ind}, variação {direcao} de {pct(var)} (de {fmt_sem_rs(v_ant)} para {fmt_sem_rs(v_atual)}).</li>")
                    
                    if textos:
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # Gráfico de barras (igual ao BP)
                    labels = ["Receita Realizada", "Despesa Empenhada", "Superávit/Déficit", "Restos a Pagar", "Receita Orçada", "Despesa Orçada"]
                    atual_vals = [
                        atual.get('receita_realizada', 0),
                        atual.get('despesa_empenhada', 0),
                        atual.get('superavit', 0),
                        atual.get('restos_pagar', 0),
                        atual.get('receita_orcada', 0),
                        atual.get('despesa_orcada', 0)
                    ]
                    ant_vals = [
                        anterior.get('receita_realizada', 0),
                        anterior.get('despesa_empenhada', 0),
                        anterior.get('superavit', 0),
                        anterior.get('restos_pagar', 0),
                        anterior.get('receita_orcada', 0),
                        anterior.get('despesa_orcada', 0)
                    ]
                    html_parts.append("<div class='grafico'><canvas id='chartBO'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartBO'), {")
                    html_parts.append("type: 'bar',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                    html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                    html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                    html_parts.append("] },")
                    html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                    html_parts.append("});")
                    html_parts.append("</script>")
                
                elif nome_interno == "Análise Financeira (BF)":
                    
                    dados_bf = mod_dados.get("dados") if isinstance(mod_dados.get("dados"), dict) else {}
                    if not dados_bf or "receitas" not in dados_bf:
                        cursor.execute(
                            "SELECT resultado_json FROM historico_analise_financeira_bf WHERE periodo = %s ORDER BY id DESC LIMIT 1",
                            (periodo,)
                        )
                        row_bf = cursor.fetchone()
                        if not row_bf:
                            cursor.execute("SELECT resultado_json FROM historico_analise_financeira_bf ORDER BY id DESC LIMIT 1")
                            row_bf = cursor.fetchone()
                        if row_bf and row_bf[0]:
                            dados_bf = row_bf[0] if isinstance(row_bf[0], dict) else json.loads(row_bf[0])

                    if not dados_bf:
                        html_parts.append("<p style='color:red;'>Dados do Balan?o Financeiro n?o encontrados no PostgreSQL para este per?odo.</p>")
                    else:
                        def _par(sec, chave):
                            obj = (dados_bf.get(sec) or {}).get(chave) or {}
                            return float(obj.get("atual") or 0.0), float(obj.get("anterior") or 0.0)

                        rec_orc_atual, rec_orc_ant = _par("receitas", "total")
                        rec_corrente_atual, rec_corrente_ant = _par("receitas", "corrente")
                        rec_capital_atual, rec_capital_ant = _par("receitas", "capital")
                        rec_extra_atual, rec_extra_ant = _par("extra", "recebimentos")
                        saldo_ant_atual, saldo_ant_ant = _par("caixa", "saldo_anterior")
                        total_ing_atual = rec_orc_atual + rec_extra_atual + saldo_ant_atual
                        total_ing_ant = rec_orc_ant + rec_extra_ant + saldo_ant_ant

                        desp_orc_atual, desp_orc_ant = _par("despesas", "total")
                        desp_corrente_atual, desp_corrente_ant = _par("despesas", "corrente")
                        desp_capital_atual, desp_capital_ant = _par("despesas", "capital")
                        desp_extra_atual, desp_extra_ant = _par("extra", "pagamentos")
                        saldo_seg_atual, saldo_seg_ant = _par("caixa", "saldo_seguinte")
                        total_disp_atual = desp_orc_atual + desp_extra_atual + saldo_seg_atual
                        total_disp_ant = desp_orc_ant + desp_extra_ant + saldo_seg_ant

                        html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Movimentação financeira consolidada.</p>")
                        html_parts.append("<table><thead><tr><th>INGRESSOS</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th><th>DISPÍŠNDIOS</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        
                        html_parts.append(f"<tr><td>Receita Orçamentária</td><td class='text-right'>{fmt_sem_rs(rec_orc_atual)}</td><td class='text-right'>{fmt_sem_rs(rec_orc_ant)}</td><td class='text-right'>{pct(calc_var(rec_orc_atual, rec_orc_ant))}</td><td>Despesa Orçamentária</td><td class='text-right'>{fmt_sem_rs(desp_orc_atual)}</td><td class='text-right'>{fmt_sem_rs(desp_orc_ant)}</td><td class='text-right'>{pct(calc_var(desp_orc_atual, desp_orc_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Receitas Correntes</td><td class='text-right'>{fmt_sem_rs(rec_corrente_atual)}</td><td class='text-right'>{fmt_sem_rs(rec_corrente_ant)}</td><td class='text-right'>{pct(calc_var(rec_corrente_atual, rec_corrente_ant))}</td><td>Despesas Correntes</td><td class='text-right'>{fmt_sem_rs(desp_corrente_atual)}</td><td class='text-right'>{fmt_sem_rs(desp_corrente_ant)}</td><td class='text-right'>{pct(calc_var(desp_corrente_atual, desp_corrente_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Receitas de Capital</td><td class='text-right'>{fmt_sem_rs(rec_capital_atual)}</td><td class='text-right'>{fmt_sem_rs(rec_capital_ant)}</td><td class='text-right'>{pct(calc_var(rec_capital_atual, rec_capital_ant))}</td><td>Despesas de Capital</td><td class='text-right'>{fmt_sem_rs(desp_capital_atual)}</td><td class='text-right'>{fmt_sem_rs(desp_capital_ant)}</td><td class='text-right'>{pct(calc_var(desp_capital_atual, desp_capital_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Recebimentos Extraorçamentários</td><td class='text-right'>{fmt_sem_rs(rec_extra_atual)}</td><td class='text-right'>{fmt_sem_rs(rec_extra_ant)}</td><td class='text-right'>{pct(calc_var(rec_extra_atual, rec_extra_ant))}</td><td>Pagamentos Extraorçamentários</td><td class='text-right'>{fmt_sem_rs(desp_extra_atual)}</td><td class='text-right'>{fmt_sem_rs(desp_extra_ant)}</td><td class='text-right'>{pct(calc_var(desp_extra_atual, desp_extra_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Saldo em Espécie do ExercÍ­cio Anterior</td><td class='text-right'>{fmt_sem_rs(saldo_ant_atual)}</td><td class='text-right'>{fmt_sem_rs(saldo_ant_ant)}</td><td class='text-right'>{pct(calc_var(saldo_ant_atual, saldo_ant_ant))}</td><td>Saldo em Espécie para o ExercÍ­cio Seguinte</td><td class='text-right'>{fmt_sem_rs(saldo_seg_atual)}</td><td class='text-right'>{fmt_sem_rs(saldo_seg_ant)}</td><td class='text-right'>{pct(calc_var(saldo_seg_atual, saldo_seg_ant))}</td></tr>")
                        html_parts.append(f"<tr><td><strong>Total Geral de Ingressos</strong></td><td class='text-right'><strong>{fmt_sem_rs(total_ing_atual)}</strong></td><td class='text-right'>{fmt_sem_rs(total_ing_ant)}</td><td class='text-right'>{pct(calc_var(total_ing_atual, total_ing_ant))}</td><td><strong>Total Geral de Dispêndios</strong></td><td class='text-right'><strong>{fmt_sem_rs(total_disp_atual)}</strong></td><td class='text-right'>{fmt_sem_rs(total_disp_ant)}</td><td class='text-right'>{pct(calc_var(total_disp_atual, total_disp_ant))}</td></tr>")
                        html_parts.append("</tbody></table>")
                        
                        # Texto dinâmico
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>")
                        html_parts.append(f"<li>Receita Orçamentária: {fmt_sem_rs(rec_orc_atual)} (variação {pct(calc_var(rec_orc_atual, rec_orc_ant))})</li>")
                        html_parts.append(f"<li>Despesa Orçamentária: {fmt_sem_rs(desp_orc_atual)} (variação {pct(calc_var(desp_orc_atual, desp_orc_ant))})</li>")
                        html_parts.append(f"<li>Recebimentos Extraorçamentários: {fmt_sem_rs(rec_extra_atual)} (variação {pct(calc_var(rec_extra_atual, rec_extra_ant))})</li>")
                        html_parts.append(f"<li>Pagamentos Extraorçamentários: {fmt_sem_rs(desp_extra_atual)} (variação {pct(calc_var(desp_extra_atual, desp_extra_ant))})</li>")
                        html_parts.append(f"<li>Saldo Final: {fmt_sem_rs(saldo_seg_atual)} (variação {pct(calc_var(saldo_seg_atual, saldo_seg_ant))})</li>")
                        html_parts.append("</ul>")
                        
                        # Gráfico de barras
                        labels = ["Rec. Orçamentária", "Desp. Orçamentária", "Receb. Extra", "Pag. Extra", "Saldo Anterior", "Saldo Seguinte"]
                        vals = [rec_orc_atual, desp_orc_atual, rec_extra_atual, desp_extra_atual, saldo_ant_atual, saldo_seg_atual]
                        html_parts.append("<div class='grafico'><canvas id='chartBF'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartBF'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Valor (R$)', data: {json.dumps(vals)}, backgroundColor: ['#004b8d', '#dc3545', '#28a745', '#fd7e14', '#6c757d', '#17a2b8'] }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif nome_interno == "Análise DFC":
                    
                    dados_dfc = mod_dados.get("dados", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração do Fluxo de Caixa (método direto).</p>")
                    
                    # Textos dinâmicos de evolução
                    textos = []
                    
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            html_parts.append(f"<h3>Fluxo {tipo.title()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                    if abs(var) > 0.01:
                                        direcao = "positiva" if var > 0 else "negativa"
                                        textos.append(f"<li>Fluxo {tipo.title()} - {k.title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                            html_parts.append("</tbody></table>")
                    
                    # Apuração de Caixa
                    if "caixa" in dados_dfc:
                        html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for k, v in dados_dfc["caixa"].items():
                            if isinstance(v, dict):
                                a = v.get("atual", 0)
                                ant = v.get("anterior", 0)
                                var = calc_var(a, ant)
                                html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>Apuração de Caixa - {k.title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")
                    
                    # Textos de evolução
                    if textos:
                        html_parts.append("<h3>Evolução dos Fluxos de Caixa</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # Gráfico de barras
                    if "operacional" in dados_dfc:
                        labels = ["Ingressos Op.", "Desembolsos Op.", "LÍ­quido Op.", "Ingressos Inv.", "Desembolsos Inv.", "LÍ­quido Inv."]
                        vals = [
                            dados_dfc.get("operacional", {}).get("ingressos", {}).get("atual", 0),
                            dados_dfc.get("operacional", {}).get("desembolsos", {}).get("atual", 0),
                            dados_dfc.get("operacional", {}).get("liquido", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("ingressos", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("desembolsos", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("liquido", {}).get("atual", 0)
                        ]
                        html_parts.append("<div class='grafico' style='max-width: 400px; height: 200px; margin: 10px auto;'><canvas id='chartDFC' style='width: 100%; height: 100%;'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartDFC'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Valor (R$)', data: {json.dumps(vals)}, backgroundColor: ['#004b8d', '#dc3545', '#28a745', '#004b8d', '#dc3545', '#28a745'] }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif nome_interno == "Análise Patrimonial (DVP)":
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração das Variações Patrimoniais.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                    
                    textos = []
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = calc_var(atual, anterior)
                            
                            # Caso especial para Margem Patrimonial (adiciona %)
                            if k == "margem_patrimonial":
                                html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{atual:.2f}%</td><td class='text-right'>{anterior:.2f}%</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>Margem Patrimonial: variação {direcao} de {pct(var)} (de {anterior:.2f}% para {atual:.2f}%).</li>")
                            else:
                                html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt_sem_rs(atual)}</td><td class='text-right'>{fmt_sem_rs(anterior)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>{k.replace('_', ' ').title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(anterior)} para {fmt_sem_rs(atual)}).</li>")
                    html_parts.append("</tbody></table>")
                    
                    # Textos de evolução
                    if textos:
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # Gráfico de barras
                    labels = []
                    atual_vals = []
                    ant_vals = []
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            labels.append(k.replace('_', ' ').title())
                            atual_vals.append(v.get("atual", 0))
                            ant_vals.append(v.get("anterior", 0))
                    
                    if labels:
                        html_parts.append("<div class='grafico'><canvas id='chartDVP'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartDVP'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                        html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif "dmpl" in _norm_key(nome_interno) or "mutacoes do pl" in _norm_key(nome_interno):
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstra??o das Muta??es do Patrim?nio L?quido (DMPL) ? dados persistidos no PostgreSQL.</p>")
                    mem_dmpl = carregar_contas_memoria("DMPL", periodo) or []
                    dados_dmpl = mod_dados if isinstance(mod_dados, dict) else {}
                    linhas_dmpl = dados_dmpl.get("linhas") if isinstance(dados_dmpl.get("linhas"), list) else []
                    colunas_dmpl = dados_dmpl.get("colunas") if isinstance(dados_dmpl.get("colunas"), list) else ["Conta / Descri??o", "Saldo Inicial", "Aumentos", "Redu??es", "Saldo Final"]

                    if linhas_dmpl:
                        html_parts.append("<table><thead><tr>")
                        for h in colunas_dmpl:
                            html_parts.append(f"<th>{h}</th>")
                        html_parts.append("</tr></thead><tbody>")
                        for r in linhas_dmpl:
                            if isinstance(r, dict):
                                html_parts.append(f"<tr><td>{r.get('descricao', r.get('conta', ''))}</td><td class='text-right'>{fmt(r.get('saldo_inicial', 0))}</td><td class='text-right'>{fmt(r.get('aumentos', 0))}</td><td class='text-right'>{fmt(r.get('reducoes', 0))}</td><td class='text-right'>{fmt(r.get('saldo_final', r.get('valor', 0)))}</td></tr>")
                            elif isinstance(r, list):
                                html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
                        html_parts.append("</tbody></table>")
                    elif mem_dmpl:
                        html_parts.append("<table><thead><tr><th>CONTA / ITEM</th><th>VALOR (R$)</th></tr></thead><tbody>")
                        for m in mem_dmpl:
                            html_parts.append(f"<tr><td>{m.get('descricao') or m.get('chave')}</td><td class='text-right'>{fmt(m.get('valor', 0))}</td></tr>")
                        html_parts.append("</tbody></table>")
                    else:
                        html_parts.append("<p style='color:#666;'>Sem lan?amentos de DMPL gravados na mem?ria do banco para este per?odo.</p>")

                elif "comparativo de receitas" in _norm_key(nome_interno):
                    atual = mod_dados.get("atual") if isinstance(mod_dados.get("atual"), dict) else mod_dados
                    anterior = mod_dados.get("anterior", {})
                    periodo_atual = mod_dados.get("periodo_atual", "")
                    periodo_anterior = mod_dados.get("periodo_anterior", "")
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo consolidado de receitas.</p>")
                    
                    # ---- 1. TABELA DE INDICADORES ----
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Orçada</td><td class='text-right'>{fmt(atual.get('orcado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt(atual.get('realizado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>% Execução</td><td class='text-right'>{atual.get('percentual_total', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 2. COMPOSIÇÃO POR GRUPO ----
                    html_parts.append("<h3>Composição por Grupo</h3>")
                    html_parts.append("<table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>REALIZADO</th><th>%</th></tr></thead><tbody>")
                    for g in atual.get("grupos", []):
                        html_parts.append(f"<tr><td>{g.get('nome','')}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('orcado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('realizado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{g.get('percentual', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 3. TEXTOS DINÂMICOS ----
                    textos = []
                    orc_tot = atual.get("orcado_total", 0) or 0
                    real_tot = atual.get("realizado_total", 0) or 0
                    pct_tot = atual.get("percentual_total", 0) or 0
                    if orc_tot > 0:
                        if pct_tot >= 100:
                            textos.append(f"<li>A receita realizada de {fmt(real_tot)} superou a orçada de {fmt(orc_tot)} em {pct_tot - 100:.2f}% (execução de {pct_tot:.2f}%).</li>")
                        else:
                            textos.append(f"<li>A receita realizada de {fmt(real_tot)} ficou abaixo da orçada de {fmt(orc_tot)}, com execução de {pct_tot:.2f}%.</li>")
                    else:
                        textos.append(f"<li>Não há receita orçada cadastrada para o perÍ­odo; a receita realizada foi de {fmt(real_tot)}.</li>")
                    
                    for g in atual.get("grupos", []):
                        nome = g.get('nome', '')
                        orc = g.get('orcado', 0) or 0
                        real = g.get('realizado', 0) or 0
                        pct_g = g.get('percentual', 0) or 0
                        if orc > 0 and real > 0:
                            if pct_g >= 100:
                                textos.append(f"<li>{nome}: arrecadação de {fmt(real)} ({pct_g:.2f}% do orçado de {fmt(orc)}).</li>")
                            elif real > 0:
                                textos.append(f"<li>{nome}: arrecadação de {fmt(real)}, abaixo do orçado de {fmt(orc)} ({pct_g:.2f}%).</li>")
                        elif real > 0:
                            textos.append(f"<li>{nome}: arrecadação de {fmt(real)} sem previsão orçada.</li>")
                    
                    if textos:
                        html_parts.append("<h3>Análise de Execução</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # ---- 4. GRÍFICO DE BARRAS (Orçado x Realizado por grupo) ----
                    grupos = atual.get("grupos", [])
                    if grupos:
                        labels = [g.get('nome','') for g in grupos]
                        vals_orc = [g.get('orcado', 0) or 0 for g in grupos]
                        vals_real = [g.get('realizado', 0) or 0 for g in grupos]
                        html_parts.append("<div class='grafico' style='max-width: 500px; height: 220px; margin: 10px auto;'><canvas id='chartReceitasBarras' style='width:100%; height:100%;'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartReceitasBarras'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [")
                        html_parts.append(f"{{ label: 'Orçado', data: {json.dumps(vals_orc)}, backgroundColor: '#6c757d' }},")
                        html_parts.append(f"{{ label: 'Realizado', data: {json.dumps(vals_real)}, backgroundColor: '#004b8d' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { x: { ticks: { font: { size: 7 } } }, y: { ticks: { font: { size: 7 } } } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif "comparativo de despesas" in _norm_key(nome_interno):
                    atual = mod_dados.get("atual", {})
                    anterior = mod_dados.get("anterior", {})
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo consolidado de despesas.</p>")
                    
                    # ---- 1. TABELA DE INDICADORES ----
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Despesa Orçada</td><td class='text-right'>{fmt(atual.get('orcado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Empenhada</td><td class='text-right'>{fmt(atual.get('empenhado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Liquidada</td><td class='text-right'>{fmt(atual.get('liquidado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>% Execução</td><td class='text-right'>{atual.get('percentual_total', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 2. COMPOSIÇÃO POR GRUPO ----
                    html_parts.append("<h3>Composição por Grupo</h3>")
                    html_parts.append("<table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>EMPENHADO</th><th>LIQUIDADO</th><th>%</th></tr></thead><tbody>")
                    for g in atual.get("grupos", []):
                        html_parts.append(f"<tr><td>{g.get('nome','')}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('orcado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('empenhado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('liquidado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{g.get('percentual', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 3. TEXTOS DINÂMICOS ----
                    textos = []
                    orc_tot = atual.get("orcado_total", 0) or 0
                    emp_tot = atual.get("empenhado_total", 0) or 0
                    liq_tot = atual.get("liquidado_total", 0) or 0
                    pct_tot = atual.get("percentual_total", 0) or 0
                    if orc_tot > 0:
                        if pct_tot >= 100:
                            textos.append(f"<li>A despesa empenhada de {fmt(emp_tot)} superou a orçada de {fmt(orc_tot)} em {pct_tot - 100:.2f}% (execução de {pct_tot:.2f}%).</li>")
                        else:
                            textos.append(f"<li>A despesa empenhada de {fmt(emp_tot)} ficou abaixo da orçada de {fmt(orc_tot)}, com execução de {pct_tot:.2f}%.</li>")
                    else:
                        textos.append(f"<li>Não há despesa orçada cadastrada para o perÍ­odo; a despesa empenhada foi de {fmt(emp_tot)}.</li>")
                    
                    if liq_tot and liq_tot != emp_tot:
                        pct_liq = (liq_tot / emp_tot * 100) if emp_tot > 0 else 0
                        textos.append(f"<li>Do total empenhado, {fmt(liq_tot)} foram liquidados ({pct_liq:.2f}% do empenhado).</li>")
                    
                    for g in atual.get("grupos", []):
                        nome = g.get('nome', '')
                        orc = g.get('orcado', 0) or 0
                        emp = g.get('empenhado', 0) or 0
                        pct_g = g.get('percentual', 0) or 0
                        if orc > 0 and emp > 0:
                            if pct_g >= 100:
                                textos.append(f"<li>{nome}: empenhado de {fmt(emp)} ({pct_g:.2f}% do orçado de {fmt(orc)}).</li>")
                            else:
                                textos.append(f"<li>{nome}: empenhado de {fmt(emp)}, abaixo do orçado de {fmt(orc)} ({pct_g:.2f}%).</li>")
                        elif emp > 0:
                            textos.append(f"<li>{nome}: empenhado de {fmt(emp)} sem previsão orçada.</li>")
                    
                    if textos:
                        html_parts.append("<h3>Análise de Execução</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # ---- 4. GRÍFICO DE BARRAS (Orçado x Empenhado por grupo) ----
                    grupos = atual.get("grupos", [])
                    if grupos:
                        labels = [g.get('nome','') for g in grupos]
                        vals_orc = [g.get('orcado', 0) or 0 for g in grupos]
                        vals_emp = [g.get('empenhado', 0) or 0 for g in grupos]
                        html_parts.append("<div class='grafico' style='max-width: 500px; height: 220px; margin: 10px auto;'><canvas id='chartDespesasBarras' style='width:100%; height:100%;'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartDespesasBarras'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [")
                        html_parts.append(f"{{ label: 'Orçado', data: {json.dumps(vals_orc)}, backgroundColor: '#6c757d' }},")
                        html_parts.append(f"{{ label: 'Empenhado', data: {json.dumps(vals_emp)}, backgroundColor: '#dc3545' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { x: { ticks: { font: { size: 7 } } }, y: { ticks: { font: { size: 7 } } } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif nome_interno == "Índices de Liquidez":
                    liq = mod_dados.get("liquidez", {})
                    est = mod_dados.get("estrutura", {})
                    liq_ant = mod_dados.get("liquidez_anterior", {})
                    est_ant = mod_dados.get("estrutura_anterior", {})
                    val = mod_dados.get("valores", {})
                    val_ant = mod_dados.get("valores_anterior", {})
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Indicadores de liquidez e estrutura patrimonial (atual x anterior).</p>")
                    
                    def fmt_valor(v):
                        if v is None: return "?"
                        try:
                            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        except (TypeError, ValueError):
                            return str(v)
                    
                    def br_para_float(v):
                        if v is None: return None
                        if isinstance(v, (int, float)): return float(v)
                        s = str(v).strip().replace("R$", "").replace(" ", "")
                        if not s or s == "-": return None
                        try:
                            return float(s.replace(".", "").replace(",", "."))
                        except ValueError:
                            return None
                    
                    def fmt_var(atual_v, anterior_v):
                        a = br_para_float(atual_v)
                        b = br_para_float(anterior_v)
                        if a is None or b is None or b == 0:
                            return None, None, None
                        var = ((a - b) / abs(b)) * 100
                        return a, b, var
                    
                    def formula_liq(k):
                        c = val.get("caixa", 0)
                        ac = val.get("ativo_circulante", 0)
                        est_v = val.get("estoques", 0)
                        rlp = val.get("realizavel_lp", 0)
                        pc = val.get("passivo_circulante", 0)
                        pnc = val.get("passivo_nao_circulante", 0)
                        if k == "liquidez_imediata":
                            return f"DisponÍ­vel ({fmt_valor(c)}) / Passivo Circulante ({fmt_valor(pc)})"
                        if k == "liquidez_corrente":
                            return f"Ativo Circulante ({fmt_valor(ac)}) / Passivo Circulante ({fmt_valor(pc)})"
                        if k == "liquidez_seca":
                            return f"(Ativo Circulante ({fmt_valor(ac)}) - Estoques ({fmt_valor(est_v)})) / Passivo Circulante ({fmt_valor(pc)})"
                        if k == "liquidez_geral":
                            return f"(Ativo Circulante ({fmt_valor(ac)}) + Realizável LP ({fmt_valor(rlp)})) / (Passivo Circulante ({fmt_valor(pc)}) + Passivo Não Circulante ({fmt_valor(pnc)}))"
                        return "-"
                    
                    def formula_est(k):
                        at = val.get("ativo_total", 0)
                        pt = val.get("passivo_total", 0)
                        pc = val.get("passivo_circulante", 0)
                        pnc = val.get("passivo_nao_circulante", 0)
                        imob = val.get("imobilizado", 0)
                        pl = val.get("patrimonio_liquido", 0)
                        if k == "endividamento_geral":
                            return f"(Passivo Circulante ({fmt_valor(pc)}) + Passivo Não Circulante ({fmt_valor(pnc)})) / Ativo Total ({fmt_valor(at)})"
                        if k == "part_capital_terceiros":
                            return f"Passivo Total ({fmt_valor(pt)}) / Ativo Total ({fmt_valor(at)})"
                        if k == "imobilizacao_pl":
                            return f"Ativo Imobilizado ({fmt_valor(imob)}) / Patrimônio LÍ­quido ({fmt_valor(pl)})"
                        return "-"
                    
                    textos = []
                    labels_liq = []
                    vals_liq_atual = []
                    vals_liq_ant = []
                    
                    # ---- LIQUIDEZ ----
                    html_parts.append("<h3>Liquidez</h3>")
                    html_parts.append("<table style='table-layout: fixed; width: 100%;'><thead><tr>")
                    html_parts.append("<th style='width: 18%;'>INDICADOR</th><th style='width: 42%;'>FÓRMULA (CONTA + VALOR)</th><th style='width: 10%;'>ATUAL</th><th style='width: 10%;'>ANTERIOR</th><th style='width: 12%;'>VAR. (%)</th>")
                    html_parts.append("</tr></thead><tbody>")
                    for k, v in liq.items():
                        v_ant = liq_ant.get(k, "-")
                        a, b, var = fmt_var(v, v_ant)
                        var_str = f"{var:+.2f}%" if var is not None else "-"
                        formula = formula_liq(k)
                        nome_fmt = k.replace('_', ' ').title()
                        html_parts.append(f"<tr><td>{nome_fmt}</td><td style='font-size: 5.0pt; text-align: left;'>{formula}</td><td class='text-right'>{v}</td><td class='text-right'>{v_ant}</td><td class='text-right'>{var_str}</td></tr>")
                        if var is not None and abs(var) > 0.01:
                            direcao = "aumento" if a > b else "redução"
                            textos.append(f"<li>{nome_fmt}: {direcao} de {b:.2f} para {a:.2f} ({var:+.2f}%).</li>")
                            labels_liq.append(nome_fmt)
                            vals_liq_atual.append(a)
                            vals_liq_ant.append(b)
                    html_parts.append("</tbody></table>")
                    
                    # ---- ESTRUTURA ----
                    html_parts.append("<h3>Estrutura Patrimonial</h3>")
                    html_parts.append("<table style='table-layout: fixed; width: 100%;'><thead><tr>")
                    html_parts.append("<th style='width: 18%;'>INDICADOR</th><th style='width: 42%;'>FÓRMULA (CONTA + VALOR)</th><th style='width: 10%;'>ATUAL</th><th style='width: 10%;'>ANTERIOR</th><th style='width: 12%;'>VAR. (%)</th>")
                    html_parts.append("</tr></thead><tbody>")
                    for k, v in est.items():
                        v_ant = est_ant.get(k, "-")
                        a, b, var = fmt_var(v, v_ant)
                        var_str = f"{var:+.2f}%" if var is not None else "-"
                        formula = formula_est(k)
                        nome_fmt = k.replace('_', ' ').title()
                        html_parts.append(f"<tr><td>{nome_fmt}</td><td style='font-size: 5.0pt; text-align: left;'>{formula}</td><td class='text-right'>{v}</td><td class='text-right'>{v_ant}</td><td class='text-right'>{var_str}</td></tr>")
                        if var is not None and abs(var) > 0.01:
                            direcao = "aumento" if a > b else "redução"
                            textos.append(f"<li>{nome_fmt}: {direcao} de {b:.2f} para {a:.2f} ({var:+.2f}%).</li>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- TEXTOS DINAMICOS ----
                    if textos:
                        html_parts.append("<h3>Evolução dos Indicadores</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os perÍ­odos.</p>")
                    
                    # ---- GRAFICO DE BARRAS ----
                    
                elif "panorama" in _norm_key(nome_interno):
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Resumo executivo dos principais indicadores.</p>")
                    
                    # Funcao para formatar valores
                    def fmt_pano(v):
                        if v is None: return "-"
                        if isinstance(v, str):
                            # Se ja eh string formatada, retorna
                            return v
                        try:
                            return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        except (ValueError, TypeError):
                            return str(v)
                    
                    # Funcao para extrair valor numerico
                    def num(v):
                        if v is None: return 0
                        if isinstance(v, (int, float)): return float(v)
                        try:
                            return float(str(v).replace("R$", "").replace(".", "").replace(",", ".").strip())
                        except ValueError:
                            return 0
                    
                    # Estilo base das pilulas
                    html_parts.append("""
                    <style>
                        .pano-pill { display: inline-block; border-radius: 30px; padding: 10px 20px; margin: 5px; font-family: 'Segoe UI', Arial, sans-serif; box-shadow: 0 2px 6px rgba(0,0,0,0.15); min-width: 150px; vertical-align: top; }
                        .pano-pill .label { font-size: 7pt; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; margin-bottom: 3px; }
                        .pano-pill .value { font-size: 10pt; font-weight: bold; }
                        .pano-pill.azul { background: #004b8d; color: #fff; }
                        .pano-pill.verde { background: #28a745; color: #fff; }
                        .pano-pill.vermelho { background: #dc3545; color: #fff; }
                        .pano-pill.cinza { background: #6c757d; color: #fff; }
                        .pano-row { margin: 10px 0; }
                        .pano-titulo { font-size: 8pt; font-weight: bold; color: #003366; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase; }
                    </style>
                    """)
                    
                    # Extrai os valores
                    ativo_total = mod_dados.get("ativo_total") or mod_dados.get("ativo_total", 0)
                    passivo_total = mod_dados.get("passivo_total") or mod_dados.get("passivo_total", 0)
                    pl = mod_dados.get("patrimonio_liquido") or mod_dados.get("patrimonio_liquido", 0)
                    caixa = mod_dados.get("caixa_bp") or mod_dados.get("caixa") or mod_dados.get("caixa", 0)
                    receita = mod_dados.get("receita_realizada") or mod_dados.get("receita_realizada", 0)
                    despesa = mod_dados.get("despesa_empenhada") or mod_dados.get("despesa_empenhada", 0)
                    sup_orc = mod_dados.get("superavit_orcamentario") or mod_dados.get("superavit_orcamentario", 0)
                    sup_patr = mod_dados.get("superavit_patrimonial") or mod_dados.get("superavit_patrimonial", 0)
                    sup_fin = mod_dados.get("superavit_financeiro") or mod_dados.get("superavit_financeiro", 0)
                    
                    # Se veio no formato "dados" aninhado
                    if isinstance(mod_dados.get("dados"), dict):
                        d = mod_dados["dados"]
                        ativo_total = d.get("ativo_total", ativo_total)
                        passivo_total = d.get("passivo_total", passivo_total)
                        pl = d.get("patrimonio_liquido", pl)
                        caixa = d.get("caixa", caixa)
                        receita = d.get("receita_realizada", receita)
                        despesa = d.get("despesa_empenhada", despesa)
                        sup_orc = d.get("superavit_orcamentario", sup_orc)
                        sup_patr = d.get("superavit_patrimonial", sup_patr)
                        sup_fin = d.get("superavit_financeiro", sup_fin)
                    
                    # Linha 1: Balanco Patrimonial
                    html_parts.append("<div class='pano-titulo'>Balanço Patrimonial</div>")
                    html_parts.append("<div class='pano-row'>")
                    html_parts.append(f"<div class='pano-pill azul'><div class='label'>Ativo Total</div><div class='value'>{fmt_pano(ativo_total)}</div></div>")
                    html_parts.append(f"<div class='pano-pill cinza'><div class='label'>Passivo Total</div><div class='value'>{fmt_pano(passivo_total)}</div></div>")
                    html_parts.append(f"<div class='pano-pill verde'><div class='label'>Patrimônio LÍ­quido</div><div class='value'>{fmt_pano(pl)}</div></div>")
                    html_parts.append(f"<div class='pano-pill azul'><div class='label'>Caixa</div><div class='value'>{fmt_pano(caixa)}</div></div>")
                    html_parts.append("</div>")
                    
                    # Linha 2: Resultados
                    html_parts.append("<div class='pano-titulo'>Resultados e Superávits</div>")
                    html_parts.append("<div class='pano-row'>")
                    html_parts.append(f"<div class='pano-pill azul'><div class='label'>Receita Realizada</div><div class='value'>{fmt_pano(receita)}</div></div>")
                    html_parts.append(f"<div class='pano-pill vermelho'><div class='label'>Despesa Empenhada</div><div class='value'>{fmt_pano(despesa)}</div></div>")
                    html_parts.append("</div>")
                    html_parts.append("<div class='pano-row'>")
                    # Superavits com cor condicional
                    def cor_superavit(v):
                        n = num(v)
                        return "verde" if n >= 0 else "vermelho"
                    html_parts.append(f"<div class='pano-pill {cor_superavit(sup_orc)}'><div class='label'>Superávit Orçamentário</div><div class='value'>{fmt_pano(sup_orc)}</div></div>")
                    html_parts.append(f"<div class='pano-pill {cor_superavit(sup_patr)}'><div class='label'>Superávit Patrimonial</div><div class='value'>{fmt_pano(sup_patr)}</div></div>")
                    html_parts.append(f"<div class='pano-pill {cor_superavit(sup_fin)}'><div class='label'>Superávit Financeiro</div><div class='value'>{fmt_pano(sup_fin)}</div></div>")
                    html_parts.append("</div>")
                    
                    # Texto dinamico explicativo
                    textos = []
                    if num(sup_orc) < 0:
                        textos.append(f"<li>O resultado orçamentário apresentou déficit de {fmt_pano(abs(num(sup_orc)))}.</li>")
                    elif num(sup_orc) > 0:
                        textos.append(f"<li>O resultado orçamentário apresentou superávit de {fmt_pano(sup_orc)}.</li>")
                    
                    if num(sup_patr) > 0:
                        textos.append(f"<li>O resultado patrimonial foi positivo em {fmt_pano(sup_patr)}.</li>")
                    elif num(sup_patr) < 0:
                        textos.append(f"<li>O resultado patrimonial foi negativo em {fmt_pano(abs(num(sup_patr)))}.</li>")
                    
                    if num(sup_fin) > 0:
                        textos.append(f"<li>O superávit financeiro foi de {fmt_pano(sup_fin)}.</li>")
                    elif num(sup_fin) < 0:
                        textos.append(f"<li>O déficit financeiro foi de {fmt_pano(abs(num(sup_fin)))}.</li>")
                    
                    if textos:
                        html_parts.append("<h3>Análise dos Resultados</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                
                
                elif nome_interno == "Análise por Centro de Custos":
                    centros = mod_dados.get("centros", [])
                    centros_ant = mod_dados.get("centros_anterior", [])
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Distribuição das despesas (Atual vs. Anterior)</p>")
                    
                    # --- TABELA ---
                    html_parts.append("<table><thead><tr><th>CENTRO DE CUSTO</th><th>ATUAL</th><th>ANTERIOR</th><th>VARIAÇÃO</th></tr></thead><tbody>")
                    for c in centros:
                        nome = c.get('nome', '')
                        valor = c.get('valor', 0)
                        ant = 0
                        for ca in centros_ant:
                            if ca.get('nome') == nome:
                                ant = ca.get('valor', 0)
                                break
                        var = ((valor - ant) / ant * 100) if ant > 0 else 0
                        cor_var = '#28a745' if var >= 0 else '#dc3545'
                        html_parts.append(f"<tr><td>{nome}</td><td class='text-right'>{fmt(valor)}</td><td class='text-right'>{fmt(ant)}</td><td class='text-right' style='color:{cor_var}; font-weight:bold;'>{var:+.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # Texto do maior centro de custo
                    if centros:
                        maior = max(centros, key=lambda x: x.get('valor', 0))
                        html_parts.append(f"<p class='texto-dinamico'>O maior centro de custo é <strong>{maior.get('nome')}</strong> com {fmt(maior.get('valor'))}.</p>")
                    
                    # --- GRÍFICO ESTILO MODELO ---
                    if centros:
                        centros_ordenados = sorted(centros, key=lambda x: x.get('valor', 0), reverse=True)
                        labels = []
                        vals_atual = []
                        vals_ant = []
                        
                        for c in centros_ordenados:
                            nome_completo = c.get('nome', '')
                            # Abrevia o nome para exibição (ex: "AF 01 Fisc")
                            partes = nome_completo.split(' - ')
                            if len(partes) >= 2:
                                # Pega a parte do meio e a última parte (abreviada)
                                meio = partes[1].split(' ')[:2]  # Ex: "AF 01"
                                nome_abrev = ' '.join(meio)
                            else:
                                nome_abrev = nome_completo[:15]
                            
                            labels.append(nome_abrev)
                            vals_atual.append(c.get('valor', 0))
                            
                            ant_c = 0
                            for ca in centros_ant:
                                if ca.get('nome') == nome_completo:
                                    ant_c = ca.get('valor', 0)
                                    break
                            vals_ant.append(ant_c)
                        
                        # Calcula as variações para mostrar em cima
                        variacoes = []
                        for i in range(len(vals_atual)):
                            if vals_ant[i] > 0:
                                variacoes.append(((vals_atual[i] - vals_ant[i]) / vals_ant[i]) * 100)
                            else:
                                variacoes.append(0)
                        
                        html_parts.append("<h3>Distribuição por Centro de Custo</h3>")
                        html_parts.append("<div class='grafico' style='max-width: 750px; height: 350px; margin: 15px auto;'><canvas id='chartCentroCustos' style='width:100%; height:100%;'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartCentroCustos'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [")
                        html_parts.append(f"{{ label: 'Atual', data: {json.dumps(vals_atual)}, backgroundColor: '#004b8d', borderRadius: 4, barPercentage: 0.8, categoryPercentage: 0.8 }},")
                        html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(vals_ant)}, backgroundColor: '#adb5bd', borderRadius: 4, barPercentage: 0.8, categoryPercentage: 0.8 }}")
                        html_parts.append("] },")
                        html_parts.append(f"""
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: {{ padding: {{ top: 30 }} }},
                            plugins: {{
                                legend: {{ position: 'top', labels: {{ font: {{ size: 9 }}, usePointStyle: true, pointStyle: 'rectRounded' }} }},
                                tooltip: {{
                                    backgroundColor: '#003366',
                                    titleFont: {{ size: 10, weight: 'bold' }},
                                    bodyFont: {{ size: 9 }},
                                    padding: 10,
                                    cornerRadius: 6,
                                    callbacks: {{
                                        label: function(ctx) {{
                                            return ctx.dataset.label + ': R$ ' + ctx.raw.toLocaleString('pt-BR', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                                        }}
                                    }}
                                }}
                            }},
                            scales: {{
                                x: {{
                                    grid: {{ display: false }},
                                    ticks: {{ font: {{ size: 7 }}, maxRotation: 0, minRotation: 0 }}
                                }},
                                y: {{
                                    beginAtZero: true,
                                    grid: {{ color: 'rgba(0,0,0,0.05)' }},
                                    ticks: {{
                                        font: {{ size: 8 }},
                                        callback: function(value) {{
                                            if (value >= 1000000) return 'R$ ' + (value/1000000).toFixed(0) + 'M';
                                            if (value >= 1000) return 'R$ ' + (value/1000).toFixed(0) + 'K';
                                            return 'R$ ' + value;
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        """)
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                elif "custo de pessoal" in _norm_key(nome_interno):
                    # Valores do JSON
                    rcl_atual = mod_dados.get("rcl_atual", 0) or 0
                    rcl_anterior = mod_dados.get("rcl_anterior", 0) or 0
                    rcl_total = mod_dados.get("rcl_total", 0) or 0
                    pessoal_atual = mod_dados.get("pessoal_atual", 0) or 0
                    pessoal_anterior = mod_dados.get("pessoal_anterior", 0) or 0
                    pessoal_total = mod_dados.get("pessoal_total", 0) or 0
                    outras_atual = mod_dados.get("outras_atual", 0) or 0
                    outras_anterior = mod_dados.get("outras_anterior", 0) or 0
                    outras_total = mod_dados.get("outras_total", 0) or 0
                    terc_atual = mod_dados.get("terc_atual", 0) or 0
                    terc_anterior = mod_dados.get("terc_anterior", 0) or 0
                    terc_total = mod_dados.get("terc_total", 0) or 0
                    custo_atual = mod_dados.get("custo_atual", 0) or 0
                    custo_anterior = mod_dados.get("custo_anterior", 0) or 0
                    custo_total = mod_dados.get("custo_total", 0) or 0
                    limite_total = mod_dados.get("limite_total", 0) or 0
                    margem_total = mod_dados.get("margem_disponivel_total", 0) or 0
                    pct_custo = mod_dados.get("pct_custo_total", 0) or 0
                    faixa_controle = mod_dados.get("faixa_controle", "N/A") or "N/A"
                    faixa_cor = mod_dados.get("faixa_cor", "success") or "success"
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Custo de pessoal x limite legal (Resolução Cofen 814/2026).</p>")
                    
                    # --- TABELA 1: COMPOSIÇÃO DO CUSTO ---
                    html_parts.append("<h3>Composição do Custo</h3>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>TOTAL</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Pessoal e Encargos</td><td class='text-right'>{fmt(pessoal_atual)}</td><td class='text-right'>{fmt(pessoal_anterior)}</td><td class='text-right'>{fmt(pessoal_total)}</td></tr>")
                    html_parts.append(f"<tr><td>Outras Despesas Variáveis</td><td class='text-right'>{fmt(outras_atual)}</td><td class='text-right'>{fmt(outras_anterior)}</td><td class='text-right'>{fmt(outras_total)}</td></tr>")
                    html_parts.append(f"<tr><td>Terceirização</td><td class='text-right'>{fmt(terc_atual)}</td><td class='text-right'>{fmt(terc_anterior)}</td><td class='text-right'>{fmt(terc_total)}</td></tr>")
                    html_parts.append(f"<tr style='font-weight:bold; background:#e9ecef;'><td>CUSTO TOTAL (Bruto)</td><td class='text-right'>{fmt(custo_atual)}</td><td class='text-right'>{fmt(custo_anterior)}</td><td class='text-right'>{fmt(custo_total)}</td></tr>")
                    html_parts.append(f"<tr><td>RCL Total (12 meses)</td><td class='text-right'>{fmt(rcl_atual)}</td><td class='text-right'>{fmt(rcl_anterior)}</td><td class='text-right'>{fmt(rcl_total)}</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # --- TABELA 2: LIMITE E MARGEM ---
                    html_parts.append("<h3>Limite e Margem</h3>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Limite Legal Aplicável</td><td class='text-right'>{fmt(limite_total)}</td></tr>")
                    html_parts.append(f"<tr><td>Margem DisponÍ­vel</td><td class='text-right'>{fmt(margem_total)}</td></tr>")
                    html_parts.append(f"<tr><td>% Custo sobre RCL</td><td class='text-right' style='font-weight:bold;'>{pct_custo:.2f}%</td></tr>")
                    html_parts.append(f"<tr><td>Faixa de Controle</td><td class='text-right' style='color:#{('28a745' if faixa_cor == 'success' else ('dc3545' if faixa_cor == 'danger' else 'ffc107'))}; font-weight:bold;'>{faixa_controle}</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # --- TABELA 3: APURAÇÃO CONSOLIDADA ---
                    html_parts.append("<h3>Apuração Consolidada 12 meses</h3>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR (R$)</th><th>% DA RCL</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Corrente LÍ­quida (RCL)</td><td class='text-right'>{fmt(rcl_total)}</td><td class='text-right'>100,00%</td></tr>")
                    html_parts.append(f"<tr><td>(-) Custo de Pessoal (Bruto)</td><td class='text-right'>{fmt(custo_total)}</td><td class='text-right'>{pct_custo:.2f}%</td></tr>")
                    pct_margem = (margem_total / rcl_total * 100) if rcl_total > 0 else 0
                    html_parts.append(f"<tr><td>(=) Margem DisponÍ­vel (Limite - Custo)</td><td class='text-right'>{fmt(margem_total)}</td><td class='text-right'>{pct_margem:.2f}%</td></tr>")
                    html_parts.append(f"<tr><td>Limite Resolução Cofen 814/2026 (50,00% da RCL)</td><td class='text-right'>{fmt(limite_total)}</td><td class='text-right'>50,00%</td></tr>")
                    html_parts.append(f"<tr style='font-weight:bold;'><td>Situação (COFEN)</td><td class='text-right'></td><td class='text-right'>{pct_custo:.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    
                    # --- TEXTO DINÂMICO FINAL ---
                    if pct_custo <= 50:
                        html_parts.append(f"<p class='texto-dinamico'><strong>Análise:</strong> O custo de pessoal representa {pct_custo:.2f}% da RCL, estando dentro do limite legal de 50% (margem disponÍ­vel de {fmt(margem_total)}). Situação: {faixa_controle}.</p>")
                    else:
                        html_parts.append(f"<p class='texto-dinamico'><strong>Análise:</strong> O custo de pessoal representa {pct_custo:.2f}% da RCL, acima do limite legal de 50%. Excesso de {fmt(custo_total - limite_total)}. Situação: {faixa_controle}.</p>")
                
                
                
                
                elif nome_interno == "Conferência das Demonstrações":
                    analises = mod_dados.get("analises", [])
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Verificação da consistência das demonstrações contábeis.</p>")
                    for a in analises:
                        html_parts.append(f"<h3>{a.get('titulo', '')}</h3>")
                        html_parts.append(f"<p style='font-size: 7.6pt;'>{a.get('conceito', '')}</p>")
                        html_parts.append("<table><thead><tr><th>ITEM</th><th>VALOR</th></tr></thead><tbody>")
                        for t in a.get("tabela", []):
                            html_parts.append(f"<tr><td>{t.get('label','')}</td><td class='text-right'>{t.get('valor','')}</td></tr>")
                        html_parts.append("</tbody></table>")
                        html_parts.append(f"<p style='font-size: 7.6pt;'><strong>Status:</strong> {a.get('status','')} - {a.get('mensagem','')}</p>")
                
            except Exception as e:
                html_parts.append(f"<p style='color:red;'>Erro: {str(e)}</p>")
        
        # ============================================================
        # 15. PARECER DO CONTADOR (com dados do contador)
        # ============================================================
        html_parts.append("<div class='page-break'></div>")
        html_parts.append("<h2>15. Parecer do Contador</h2>")
        html_parts.append("<div class='parecer'>")
        
        html_parts.append("<h3>1. Situação Patrimonial e Financeira — Sólida e Equilibrada</h3>")
        html_parts.append("<p>A entidade apresenta solidez financeira notável, evidenciada por um caixa elevado que suporta integralmente seus gastos operacionais. Os Í­ndices de liquidez demonstram capacidade excepcional de honrar compromissos de curto e longo prazos. O endividamento geral confirma uma estrutura de capital conservadora.</p>")
        
        html_parts.append("<h3>2. Desempenho Orçamentário — Estabilidade</h3>")
        html_parts.append("<p>As receitas e despesas orçamentárias realizadas mantiveram-se no mesmo patamar do exercÍ­cio anterior, indicando previsibilidade e controle na execução orçamentária. Não se observam desvios relevantes que comprometam o equilÍ­brio fiscal.</p>")
        
        html_parts.append("<h3>3. Geração de Caixa — Evolução Positiva</h3>")
        html_parts.append("<p>A Demonstração dos Fluxos de Caixa (DFC) revela geração lÍ­quida de caixa positiva, reforçando a capacidade de autofinanciamento e a consistência operacional da entidade.</p>")
        
        html_parts.append("<h3>4. Resultado Patrimonial — Crescimento Contábil Relevante</h3>")
        html_parts.append("<p>O resultado patrimonial registrou acréscimo significativo. Contudo, trata-se de resultado contábil, sem reflexo financeiro imediato, devendo ser interpretado com cautela, pois decorre de variações patrimoniais.</p>")
        
        html_parts.append("<h3>5. Estrutura de Custos — Conformidade e Eficiência</h3>")
        html_parts.append("<p>O custo de pessoal encontra-se dentro do limite legal de 50% da RCL, com margem significativa, em conformidade com os limites da Resolução Cofen 814/2026.</p>")
        
        html_parts.append("<h3>6. Integridade das Demonstrações</h3>")
        html_parts.append("<p>Verificou-se a integridade das demonstrações contábeis, que se apresentam adequadas e em conformidade com os princÍ­pios e normas aplicáveis, conferindo confiabilidade Í s informações analisadas.</p>")
        
        html_parts.append("<h3>Considerações Finais</h3>")
        html_parts.append("<p>O Cofen demonstra excelente saúde financeira e patrimonial, com liquidez amplamente favorável, endividamento irrisório, geração de caixa positiva e crescimento contábil expressivo. A execução orçamentária é estável e o custo com pessoal encontra-se dentro dos limites legais.</p>")
        
        html_parts.append("<p><strong>Conclusão:</strong> As demonstrações contábeis refletem equilÍ­brio, solidez e conformidade, não havendo indÍ­cios de risco financeiro ou descumprimento de limites legais.</p>")
        
        html_parts.append("</div>")
        html_parts.append("<div class='assinatura'><div class='linha'></div>")
        html_parts.append(f"<p>{contador_nome}<br>CRC: {contador_crc} / UF: {contador_uf}<br>CPF: {contador_cpf}</p>")
        html_parts.append("</div>")
        html_parts.append("</body></html>")
        
        html = "".join(html_parts)
        
        cursor.close()
        conn.close()
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html, wait_until='networkidle')
            pdf_bytes = page.pdf(format='A4', print_background=True)
            browser.close()
        
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{periodo}.pdf"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=f"Erro ao gerar PDF: {str(e)}", status_code=500, media_type="text/plain")
