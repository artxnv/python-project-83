import psycopg2
from psycopg2 import extras
from datetime import datetime


def get_db_connection(database_url):
    """Создаёт новое соединение с базой данных."""
    conn = psycopg2.connect(database_url)
    conn.cursor_factory = extras.DictCursor
    return conn


def get_url_by_id(database_url, id):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT name FROM urls WHERE id = %s', (id,))
            result = cur.fetchone()
        return result['name'] if result else None


def insert_url_check(database_url, url_id, data):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (url_id, data['status_code'], data['h1'], data['title'], data['description'], datetime.now())
            )
            conn.commit()


def check_url_exists(database_url, url):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name = %s', (url,))
            return cur.fetchone()


def insert_new_url(database_url, url):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
                (url, datetime.now())
            )
            result = cur.fetchone()['id']
            conn.commit()
        return result


def get_all_urls(database_url):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT u.id, u.name, MAX(c.created_at) AS last_checked, MAX(c.status_code) AS last_status_code
                FROM urls u
                LEFT JOIN url_checks c ON u.id = c.url_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
            ''')
            return cur.fetchall()


def get_url_details(database_url, url_id):
    with get_db_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s', (url_id,))
            url_data = cur.fetchone()
            cur.execute('SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC', (url_id,))
            checks = cur.fetchall()
        return url_data, checks
