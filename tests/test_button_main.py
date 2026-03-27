"""
Тест: найти кнопку на основной странице (вне iframe)
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def test_button():
    """Проверить, где находится кнопка Купить"""
    print("🔍 ПОИСК КНОПКИ НА ОСНОВНОЙ СТРАНИЦЕ")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    
    try:
        # Открываем Вишневый сад
        print("\n📂 Открываю Вишневый сад...")
        bot.open_play_page(838)
        
        # НЕ переключаемся в iframe — остаёмся на основной странице
        print("\n🔍 Ищу кнопку 'Купить' на основной странице...")
        
        # Пробуем разные селекторы
        selectors = [
            "button.button.buy",
            "button.buy",
            ".button.buy",
            "button[type='button'].buy",
            "div.buttonGroup button",
            ".buttonGroup button",
            "a.uk-button-primary",
            ".uk-button-primary",
            "a:contains('Купить')",
            "//a[contains(text(), 'Купить')]",
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
            except Exception as e:
                print(f"Ошибка с селектором {selector}: {e}")
        
        # Ищем все кнопки на странице
        print("\n🔍 Все кнопки на основной странице:")
        all_buttons = bot.driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(all_buttons):
            text = btn.text.strip()
            if text:
                print(f"  {i+1}. Текст: '{text}', классы: {btn.get_attribute('class')}")
        
        # Ищем все ссылки с текстом "Купить"
        print("\n🔍 Все ссылки с текстом 'Купить':")
        all_links = bot.driver.find_elements(By.XPATH, "//a[contains(text(), 'Купить')]")
        for i, link in enumerate(all_links):
            print(f"  {i+1}. Текст: '{link.text}', href: {link.get_attribute('href')}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\n\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_button()