import sqlite3
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
DB_PATH = project_root / 'data' / 'db' /'hr_brand.sqlite'
CSV_PATH = project_root / 'data' / 'processed' / 'vacancies_processed.csv'
SCHEMA_PATH = project_root / 'sql' / 'schema.sql'

def create_tables(conn):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

def load_csv_to_db(conn):
    df = pd.read_csv(CSV_PATH)
    df.to_sql("vacancies", conn, if_exists="replace", index=False)
    return


if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        load_csv_to_db(conn)
        count = conn.execute("SELECT COUNT(*) FROM vacancies").fetchone()[0]
        print(f"Загружено {count} строк в {DB_PATH}")
    finally:
        conn.close()