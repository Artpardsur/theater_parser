#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser.edge_bot import EdgeTheaterBot

def main():
    print("🎭 Театральный парсер")
    print("=" * 40)
    
    bot = EdgeTheaterBot(headless=False)
    
    seats_config = {
        'preferred_rows': [5, 6, 7],
        'seats_per_side': 2
    }
    
<<<<<<< Updated upstream
    # Пробуем найти и забронировать
    result = bot.run_auto(play_name="Вишневый сад", seats_config=seats_config)
=======
    # ========== ВЫБЕРИТЕ РЕЖИМ ==========
    
    # РЕЖИМ 1: Поиск по названию (автоматически находит ID)
    print("🔍 Режим: автоматический поиск спектакля 'Вишневый сад'")
    result = bot.run_auto(play_name="Вишневый сад", seats_config=seats_config)
    
    # РЕЖИМ 2: По конкретному ID (быстрее, если ID известен)
    # print("🎯 Режим: бронирование по ID 714 (Крыша поехала)")
    # result = bot.run(session_id=714, seats=[{'row': 5, 'seat': 1}, {'row': 5, 'seat': 2}])
    
    # ====================================
>>>>>>> Stashed changes
    
    if result:
        print(f"\n✅ Ссылка на оплату: {result}")
    else:
        print("\n❌ Билеты не найдены")
    
    input("\nНажмите Enter, чтобы закрыть...")
    bot.close()

if __name__ == "__main__":
    main()