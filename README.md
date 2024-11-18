### Hexlet tests and linter status:
[![Actions Status](https://github.com/artxnv/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/artxnv/python-project-83/actions)

[![Flake8](https://github.com/artxnv/python-project-83/actions/workflows/main.yml/badge.svg)](https://github.com/artxnv/python-project-83/actions/workflows/main.yml)


Анализатор страниц
Page Analyzer — это веб-приложение Flask, которое позволяет пользователям анализировать веб-страницы на предмет эффективности SEO. Приложение проверяет доступность сайтов и анализирует такие элементы, как заголовки, описания и теги H1.

Функции
Проверка доступности URL.
Анализ тегов title и description.
Отображение результатов проверки в пользовательском интерфейсе.
Демонстрация
Посмотреть приложение в действии можно по этой ссылке: Page Analyzer Demo

Technologies
Python
Flask
PostgreSQL
HTML/CSS
Bootstrap for frontend
Poetry for dependency management
Необходимые условия
Убедитесь, что у вас установлены Python, Poetry и PostgreSQL.

Установка и эксплуатация
Используйте инструмент для упрощения процесса установки и запуска:Makefile

git clone https://github.com/artxnv/python-project-83
cd python-project-83

## Configuration
Before running the application, you need to set up your environment variables. Duplicate the `.env.example` file and rename it to `.env`. Then, modify it with your actual data for the following variables:
- `SECRET_KEY`: a secret key for your application.
- `DATABASE_URL`: the connection string for your PostgreSQL database, formatted as `postgresql://username:password@localhost:5432/database_name`.

# Install dependencies
make install

# Run the local development server
make dev

# Run the production server
make start
Тестирование
Чтобы запустить тесты, используйте следующую команду:

make lint  # Code linting
