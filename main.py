#!/usr/bin/env python
"""
Главный файл для запуска театрального парсера
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser.edge_bot import EdgeTheaterBot


def main():
    """Запуск бота"""
    print("🎭 Театральный парсер")
    print("=" * 40)
    
    # Создаем бота (видимый режим для отладки)
    bot = EdgeTheaterBot(headless=False)
    
    # Настройка мест
    seats_config = {
        'preferred_rows': [5, 6, 7],  # предпочитаемые ряды
        'seats_per_side': 2           # нужно 2 места рядом
    }
    
    # ========== ВЫБЕРИТЕ РЕЖИМ ==========
    
    # РЕЖИМ 1: Поиск по названию (автоматически находит ID)
    print("🔍 Режим: автоматический поиск спектакля 'Крыша поехала'")
    result = bot.run_auto(play_name="Крыша поехала", seats_config=seats_config)
    
    # РЕЖИМ 2: По конкретному ID (быстрее, если ID известен)
    # print("🎯 Режим: бронирование по ID 714 (Крыша поехала)")
    # result = bot.run(session_id=714, seats=[{'row': 5, 'seat': 1}, {'row': 5, 'seat': 2}])
    
    # ====================================
    
    if result:
        print(f"\n{'='*50}")
        print(f"🎉 УСПЕХ! Билеты забронированы!")
        print(f"🔗 Ссылка для оплаты: {result}")
        print(f"{'='*50}")
    else:
        print(f"\n❌ Билеты не найдены")
    
    input("\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    main()