from flask import Flask, request, render_template, redirect, url_for, flash
from .db import (get_db_connection, get_url_by_id, insert_url_check,
                 check_url_exists, insert_new_url, get_all_urls, get_url_details,
                 configure_database_url)
import validators
from dotenv import load_dotenv
import os
from .utils import format_date, normalize_url
from .utils import fetch_and_parse_url


# Загрузка переменных окружения
load_dotenv()

# Настройка приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.jinja_env.filters['date'] = format_date

# Передача конфигурации базы данных
configure_database_url(os.getenv('DATABASE_URL'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    with get_db_connection() as conn:
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    raw_url = request.form['url']
    if not validators.url(raw_url):
        flash('Некорректный URL', 'alert-danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(raw_url)
    with get_db_connection() as conn:
        try:
            existing_url = check_url_exists(conn, normalized_url)
            if existing_url:
                flash('Страница уже существует', 'alert-info')
                redirect_url = redirect(url_for('url_details', id=existing_url['id']))
            else:
                url_id = insert_new_url(conn, normalized_url)
                conn.commit()
                flash('Страница успешно добавлена', 'alert-success')
                redirect_url = redirect(url_for('url_details', id=url_id))
        except Exception as e:
            conn.rollback()
            flash(f'Произошла ошибка при добавлении URL: {e}', 'alert-danger')
            redirect_url = render_template('index.html'), 422

    return redirect_url


@app.route('/urls')
def urls():
    with get_db_connection() as conn:
        urls_data = get_all_urls(conn)
    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def url_details(id):
    with get_db_connection() as conn:
        url_data, checks = get_url_details(conn, id)
    return render_template('url.html', url=url_data, checks=checks)
