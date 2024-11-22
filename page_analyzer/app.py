from flask import Flask, request, render_template, redirect, url_for, flash, g
from .db import get_url_by_id, insert_url_check, check_url_exists, insert_new_url, get_all_urls, get_url_details
import validators
from dotenv import load_dotenv
import os
from .utils import format_date, normalize_url, fetch_and_parse_url
import psycopg2
from psycopg2 import extras


# Загрузка переменных окружения
load_dotenv()


# Настройка приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.jinja_env.filters['date'] = format_date


# Установка соединения с БД перед каждым запросом
@app.before_request
def before_request():
    g.db = psycopg2.connect(app.config['DATABASE_URL'], cursor_factory=extras.DictCursor)


# Закрытие соединения после каждого запроса
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


# Маршрут для проверки URL
@app.post('/urls/<int:id>/checks')
def create_check(id):
    conn = g.db  # Берём соединение из контекста
    url = get_url_by_id(conn, id)
    if url:
        result = fetch_and_parse_url(url)
        if 'error' not in result:
            insert_url_check(conn, id, result)
            flash('Страница успешно проверена', 'alert-success')
        else:
            flash(result['error'], 'alert-danger')
    else:
        flash('URL не найден', 'alert-danger')

    return redirect(url_for('url_details', id=id))


# Остальные маршруты
@app.get('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    raw_url = request.form['url']
    if not validators.url(raw_url):
        flash('Некорректный URL', 'alert-danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(raw_url)
    existing_url = check_url_exists(g.db, normalized_url)
    if existing_url:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_details', id=existing_url['id']))

    url_id = insert_new_url(g.db, normalized_url)
    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('url_details', id=url_id))


@app.get('/urls')
def urls():
    urls_data = get_all_urls(g.db)
    return render_template('urls.html', urls=urls_data)


@app.get('/urls/<int:id>')
def url_details(id):
    url_data, checks = get_url_details(g.db, id)
    return render_template('url.html', url=url_data, checks=checks)
