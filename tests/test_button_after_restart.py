"""
Тест: найти кнопку после перезапуска браузера
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def test_button():
    """Проверить, где находится кнопка"""
    print("🔍 ПОИСК КНОПКИ ПОСЛЕ ПЕРЕЗАПУСКА")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    
    try:
        # Открываем Вишневый сад
        print("\n📂 Открываю Вишневый сад...")
        bot.open_play_page(838)
        
        print("🔄 Переключаюсь в iframe...")
        bot.switch_to_hall_iframe()
        time.sleep(3)
        
        print("\n🔍 Ищу кнопку 'Купить'...")
        
        # Пробуем разные селекторы
        selectors = [
            "button.button.buy",
            "button.buy",
            ".button.buy",
            "button[type='button'].buy",
            "div.buttonGroup button",
            ".buttonGroup button",
            "button:contains('Купить')",
            "//button[contains(text(), 'Купить')]"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    elements = bot.driver.find_elements(By.XPATH, selector)
                else:
                    elements = bot.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"\n✅ Найдено {len(elements)} элементов по селектору: {selector}")
                    for i, el in enumerate(elements[:3]):
                        print(f"   {i+1}. Текст: '{el.text}'")
                        print(f"      Классы: {el.get_attribute('class')}")
                        print(f"      Видим: {el.is_displayed()}")
                        print(f"      Доступен: {el.is_enabled()}")
            except Exception as e:
                print(f"Ошибка с селектором {selector}: {e}")
        
        # Проверяем, что вообще есть в iframe
        print("\n📋 Содержимое iframe (первые 500 символов):")
        html = bot.driver.page_source
        print(html[:500])
        
        # Ищем все кнопки
        print("\n🔍 Все кнопки в iframe:")
        all_buttons = bot.driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(all_buttons):
            print(f"  {i+1}. Текст: '{btn.text}', классы: {btn.get_attribute('class')}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\n\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_button()