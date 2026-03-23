"""
Проверить, когда обновлялась страница
"""

import requests

def check_last_modified(url):
    """Проверить заголовок Last-Modified"""
    try:
        response = requests.head(url, allow_redirects=True)
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        # Проверяем заголовки
        last_modified = response.headers.get('last-modified')
        if last_modified:
            print(f"📅 Last-Modified: {last_modified}")
        else:
            print("❌ Заголовок Last-Modified отсутствует")
        
        # Другие полезные заголовки
        cache_control = response.headers.get('cache-control')
        if cache_control:
            print(f"📦 Cache-Control: {cache_control}")
        
        etag = response.headers.get('etag')
        if etag:
            print(f"🔖 ETag: {etag}")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🔍 ПРОВЕРКА ВРЕМЕНИ ОБНОВЛЕНИЯ")
    print("=" * 50)
    
    check_last_modified("https://stavteatr.ru/p/playbill")
    print()
    check_last_modified("https://quicktickets.ru/stavropol-teatr-dramy-lermontova")