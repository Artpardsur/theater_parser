"""
Тест: найти все места в iframe
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def test_find_seats():
    """Найти все элементы, которые могут быть местами"""
    print("🎭 ПОИСК МЕСТ В ЗАЛЕ")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    
    try:
        # Открываем Вишневый сад
        print("\n📂 Открываю Вишневый сад...")
        bot.open_play_page(838)
        
        print("🔄 Переключаюсь в iframe...")
        bot.switch_to_hall_iframe()
        time.sleep(2)
        
        print("\n🔍 Ищу элементы с атрибутами мест...")
        
        # Пробуем разные селекторы
        selectors = [
            "[data-row]",
            "[data-place]",
            "[data-seat]",
            "[data-col]",
            ".seat",
            ".place",
            "[class*='seat']",
            "[class*='place']",
            "rect",
            "circle"
        ]
        
        for selector in selectors:
            elements = bot.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"\n✅ Селектор '{selector}': {len(elements)} элементов")
                # Показываем первые 3
                for i, el in enumerate(elements[:3]):
                    html = el.get_attribute("outerHTML")[:150]
                    classes = el.get_attribute("class") or "нет классов"
                    print(f"   {i+1}. {html}")
                    print(f"      Классы: {classes}")
            else:
                print(f"❌ Селектор '{selector}': 0 элементов")
        
        # Ищем любые элементы, которые видны
        print("\n\n🔍 Ищу все видимые элементы...")
        body = bot.driver.find_element(By.TAG_NAME, "body")
        all_elements = body.find_elements(By.XPATH, ".//*")
        
        visible_elements = []
        for el in all_elements:
            if el.is_displayed():
                visible_elements.append(el)
        
        print(f"Всего видимых элементов: {len(visible_elements)}")
        
        if visible_elements:
            print("\n📋 Примеры видимых элементов:")
            for i, el in enumerate(visible_elements[:5]):
                print(f"  {i+1}. Тег: {el.tag_name}")
                print(f"     Классы: {el.get_attribute('class')}")
                print(f"     Текст: {el.text[:50]}")
                print()
        
        # Пробуем найти SVG элементы (схема часто рисуется в SVG)
        svg = bot.driver.find_elements(By.TAG_NAME, "svg")
        print(f"\n📊 Найдено SVG элементов: {len(svg)}")
        
        if svg:
            print("SVG найден! Места могут быть внутри.")
            # Ищем внутри SVG элементы мест
            for s in svg:
                rects = s.find_elements(By.TAG_NAME, "rect")
                circles = s.find_elements(By.TAG_NAME, "circle")
                print(f"  rect: {len(rects)}, circle: {len(circles)}")
                
                if rects:
                    print("\n  Пример rect:")
                    for rect in rects[:3]:
                        print(f"    {rect.get_attribute('outerHTML')[:200]}")
                
                if circles:
                    print("\n  Пример circle:")
                    for circle in circles[:3]:
                        print(f"    {circle.get_attribute('outerHTML')[:200]}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\n\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_find_seats()