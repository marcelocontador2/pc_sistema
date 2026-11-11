import sqlite3
try:
    conn = sqlite3.connect('pc_storage/banco_dados.db')
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM historico_notas_explicativas WHERE resultado_json LIKE '%Ã%'")
    print(cur.fetchone()[0])
    conn.close()
except Exception as e:
    print(0)
