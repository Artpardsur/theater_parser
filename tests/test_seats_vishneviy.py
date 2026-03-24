"""
Тест: найти любые свободные места в Вишневом саду
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def test_any_free_seats():
    """Проверить, есть ли вообще свободные места"""
    print("🎭 ПРОВЕРКА: ПОИСК ЛЮБЫХ СВОБОДНЫХ МЕСТ")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    
    try:
        # Открываем Вишневый сад
        print("\n📂 Открываю Вишневый сад (ID: 838)...")
        bot.open_play_page(838)
        
        print("🔄 Переключаюсь в iframe...")
        bot.switch_to_hall_iframe()
        time.sleep(2)
        
        print("\n🔍 Ищу все элементы, похожие на места...")
        
        # Пробуем разные селекторы
        selectors = [
            "[data-row]",
            "[data-place]",
            ".seat",
            ".place",
            "rect",
            "div[class*='seat']",
            "td"
        ]
        
        all_elements = []
        for selector in selectors:
            elements = bot.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"  Селектор '{selector}': найдено {len(elements)} элементов")
                all_elements.extend(elements)
        
        print(f"\n📊 Всего найдено элементов: {len(all_elements)}")
        
        # Анализируем найденные элементы
        free_seats = []
        
        for el in all_elements:
            try:
                # Получаем атрибуты
                html = el.get_attribute("outerHTML")
                classes = el.get_attribute("class") or ""
                
                # Проверяем, есть ли признаки места
                has_row = el.get_attribute("data-row") or el.get_attribute("row")
                has_place = el.get_attribute("data-place") or el.get_attribute("data-col") or el.get_attribute("data-seat")
                
                if has_row or has_place:
                    # Проверяем, свободно ли место
                    is_free = "busy" not in classes and "taken" not in classes and "reserved" not in classes
                    
                    if is_free:
                        free_seats.append({
                            'html': html[:200],
                            'classes': classes,
                            'row': has_row,
                            'place': has_place
                        })
            except:
                continue
        
        print(f"\n✅ Найдено потенциальных свободных мест: {len(free_seats)}")
        
        if free_seats:
            print("\n📋 Примеры свободных мест:")
            for i, seat in enumerate(free_seats[:3], 1):
                print(f"\n  {i}. HTML: {seat['html']}")
                print(f"     Классы: {seat['classes']}")
                if seat['row']:
                    print(f"     Ряд: {seat['row']}")
                if seat['place']:
                    print(f"     Место: {seat['place']}")
        else:
            print("\n❌ Свободных мест не найдено!")
            print("\n🔍 Показываю примеры всех найденных элементов:")
            for i, el in enumerate(all_elements[:5], 1):
                try:
                    html = el.get_attribute("outerHTML")[:200]
                    print(f"\n  {i}. {html}")
                except:
                    pass
        
        print("\n" + "=" * 60)
        print("💡 Совет: посмотрите в браузере, есть ли свободные места визуально?")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\n\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_any_free_seats()