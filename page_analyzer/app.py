from flask import Flask, request, render_template, redirect, url_for, flash
from .db import (get_url_by_id, insert_url_check, check_url_exists,
                 insert_new_url, get_all_urls, get_url_details)
import validators
from dotenv import load_dotenv
import os
from .utils import format_date, normalize_url, fetch_and_parse_url


# Загрузка переменных окружения
load_dotenv()

# Настройка приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.jinja_env.filters['date'] = format_date


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    url = get_url_by_id(app.config['DATABASE_URL'], id)
    if url:
        result = fetch_and_parse_url(url)
        if 'error' not in result:
            insert_url_check(app.config['DATABASE_URL'], id, result)
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
    existing_url = check_url_exists(app.config['DATABASE_URL'], normalized_url)
    if existing_url:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_details', id=existing_url['id']))

    url_id = insert_new_url(app.config['DATABASE_URL'], normalized_url)
    flash('Страница успешно добавлена', 'alert-success')
    return redirect(url_for('url_details', id=url_id))


@app.route('/urls')
def urls():
    urls_data = get_all_urls(app.config['DATABASE_URL'])
    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def url_details(id):
    url_data, checks = get_url_details(app.config['DATABASE_URL'], id)
    return render_template('url.html', url=url_data, checks=checks)
