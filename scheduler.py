"""
Планировщик для периодической проверки
"""

import time
import random
from datetime import datetime
from edge_bot import EdgeTheaterBot


def check_plays():
    """Проверить спектакли"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Проверяю спектакли...")
    
    bot = EdgeTheaterBot(headless=True)  # Фоновый режим
    
    # Проверяем Вишневый сад (ищем новые даты)
    # Нужно сначала получить список всех сеансов
    # Пока просто проверяем известный ID
    
    result = bot.run(session_id=838)
    
    if result:
        print(f"🎉 НАЙДЕН СПЕКТАКЛЬ! Ссылка: {result}")
        # Здесь можно отправить уведомление в Telegram
        return True
    
    bot.close()
    return False


def main():
    """Запуск планировщика"""
    print("🔄 Планировщик запущен. Проверка каждые 5-10 минут...")
    
    while True:
        try:
            # Случайный интервал от 5 до 10 минут (в секундах)
            interval = random.randint(5 * 60, 10 * 60)
            
            check_plays()
            
            print(f"Следующая проверка через {interval // 60} минут...")
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n👋 Планировщик остановлен")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()