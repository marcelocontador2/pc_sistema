import asyncio
import traceback
from integridade import analise_integridade
import sqlite3, json, datetime, os

async def testar():
    try:
        print("1. Iniciando analise...")
        dados = await analise_integridade('2026-TRIMESTRE-3')
        print("2. Analise concluida.")
        
        print("3. Convertendo para JSON...")
        json_resultado = json.dumps(dados)
        data_agora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        print("4. Conectando ao banco...")
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pc_storage', 'banco_dados.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("5. Executando INSERT...")
        cursor.execute("INSERT INTO historico_integridade (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)", ('2026-TRIMESTRE-3', data_agora, json_resultado))
        conn.commit()
        conn.close()
        print("6. Sucesso absoluto! Salvo no banco.")
    except Exception as e:
        print("\nERRO DETECTADO:")
        traceback.print_exc()

asyncio.run(testar())
