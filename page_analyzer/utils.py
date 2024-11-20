from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup


def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)


def normalize_url(input_url):
    url_parts = urlparse(input_url)
    normalized_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return normalized_url


def fetch_and_parse_url(url):
    """Загружает страницу по URL и извлекает её содержимое."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return {
                'title': soup.find('title').text if soup.find('title') else None,
                'h1': soup.find('h1').text if soup.find('h1') else None,
                'description': soup.find('meta', attrs={'name': 'description'})['content']
                if soup.find('meta', attrs={'name': 'description'}) else None,
                'status_code': response.status_code
            }
        else:
            return {'error': 'Произошла ошибка при проверке'}
    except requests.RequestException:
        return {'error': 'Произошла ошибка при проверке'}
