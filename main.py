#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser.edge_bot import EdgeTheaterBot

def main():
    print("🎭 Театральный парсер")
    print("=" * 60)
    print("Бот работает в свернутом режиме. При находке билетов окно появится.")
    print()
    
    # Запускаем в видимом, но свернутом режиме
    bot = EdgeTheaterBot(headless=False, minimized=True)
    
    seats_config = {
        'preferred_rows': [5, 6, 7],
        'seats_per_side': 2
    }
    
    try:
        result = bot.run_auto(play_name="Вишневый сад", seats_config=seats_config)
        
        if result:
            print(f"\n{'='*60}")
            print(f"🎉 БИЛЕТЫ НАЙДЕНЫ!")
            print(f"🔗 Ссылка для оплаты: {result}")
            print(f"{'='*60}")
        else:
            print("\n❌ Билеты не найдены")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\nНажмите Enter, чтобы закрыть...")
    bot.close()

if __name__ == "__main__":
    main()