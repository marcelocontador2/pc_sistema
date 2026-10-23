import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def testar_conexao():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tabelas = cursor.fetchall()
        print("Conexao bem-sucedida! Tabelas no banco:")
        for tabela in tabelas:
            print(f"- {tabela[0]}")
        cursor.close()
        conn.close()
    else:
        print("Falha na conexao.")

if __name__ == "__main__":
    testar_conexao()
