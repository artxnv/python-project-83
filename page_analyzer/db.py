import psycopg2
from psycopg2 import extras
from datetime import datetime

# Глобальная переменная для хранения строки подключения
DATABASE_URL = None


def configure_database_url(url):
    """Настраивает URL для подключения к базе данных."""
    global DATABASE_URL
    DATABASE_URL = url


def get_db_connection():
    """Открывает соединение с базой данных."""
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL не настроен. Используйте configure_database_url().")
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = extras.DictCursor
    return conn


def get_url_by_id(conn, id):
    with conn.cursor() as cur:
        cur.execute('SELECT name FROM urls WHERE id = %s', (id,))
        result = cur.fetchone()
    return result['name'] if result else None


def insert_url_check(conn, url_id, data):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (url_id, data['status_code'], data['h1'], data['title'], data['description'], datetime.now())
        )
        conn.commit()


def check_url_exists(conn, url):
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM urls WHERE name = %s', (url,))
        return cur.fetchone()


def insert_new_url(conn, url):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
            (url, datetime.now())
        )
        return cur.fetchone()['id']


def get_all_urls(conn):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT u.id, u.name, MAX(c.created_at) AS last_checked, MAX(c.status_code) AS last_status_code
            FROM urls u
            LEFT JOIN url_checks c ON u.id = c.url_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        ''')
        return cur.fetchall()


def get_url_details(conn, url_id):
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM urls WHERE id = %s', (url_id,))
        url_data = cur.fetchone()
        cur.execute('SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC', (url_id,))
        checks = cur.fetchall()
    return url_data, checks
