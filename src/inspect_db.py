import sqlite3
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
DB_PATH = project_root / 'data' / 'db' /'hr_brand.sqlite'

def run_query(conn, filename):
    """Читает .sql файл из sql/queries/ и возвращает DataFrame"""
    path = project_root / 'sql'/ 'queries' / filename
    sql = path.read_text(encoding='utf-8')
    return pd.read_sql(sql, conn)

if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    try:
        print('Таблицы в базе:')
        tables = conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()

        print('\nКоличество строк:')
        print(conn.execute('SELECT COUNT(*) FROM vacancies').fetchone()[0])

        # Запуск запросов
        print('\n--- 01_top_cities.sql ---')
        print(run_query(conn, '01_top_cities.sql'))

        print('\n--- 02_salary_by_experience.sql ---')
        print(run_query(conn, '02_salary_by_experience.sql'))

        print('\n--- 03_benefits_share.sql ---')
        print(run_query(conn, '03_benefits_share.sql'))

        print('\n--- 04_role_ranking.sql ---')
        print(run_query(conn, '04_role_ranking.sql'))

        print('\n--- 05_salary_vs_mean.sql ---')
        print(run_query(conn, '05_salary_vs_mean.sql'))

        print('\n--- 06_experience_distribution.sql ---')
        print(run_query(conn, '06_experience_distribution.sql'))

    finally:
        conn.close()