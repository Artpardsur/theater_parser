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
    
    # Пробуем найти и забронировать
    result = bot.run_auto(play_name="Вишневый сад", seats_config=seats_config)
    
    if result:
        print(f"\n✅ Ссылка на оплату: {result}")
    else:
        print("\n❌ Билеты не найдены")
    
    input("\nНажмите Enter, чтобы закрыть...")
    bot.close()

if __name__ == "__main__":
    main()