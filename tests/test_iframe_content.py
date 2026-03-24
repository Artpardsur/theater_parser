"""
Тест: проверить содержимое iframe
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def test_iframe_content():
    """Проверить, что внутри iframe"""
    print("🎭 ПРОВЕРКА СОДЕРЖИМОГО IFRAME")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    
    try:
        # Открываем Вишневый сад
        print("\n📂 Открываю Вишневый сад (ID: 838)...")
        bot.open_play_page(838)
        
        print("\n🔍 Ищу iframe...")
        iframes = bot.driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Найдено iframe на странице: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            print(f"\niframe {i+1}:")
            print(f"  name: {iframe.get_attribute('name')}")
            print(f"  src: {iframe.get_attribute('src')[:100]}")
        
        # Переключаемся в iframe
        print("\n🔄 Переключаюсь в iframe...")
        bot.switch_to_hall_iframe()
        
        print("\n🔍 Проверяю содержимое iframe:")
        
        # Получаем HTML внутри iframe
        html = bot.driver.page_source
        print(f"Длина HTML: {len(html)} символов")
        print(f"\nПервые 500 символов HTML внутри iframe:")
        print("-" * 60)
        print(html[:500])
        print("-" * 60)
        
        # Ищем любые элементы
        all_elements = bot.driver.find_elements(By.XPATH, "//*")
        print(f"\n📊 Всего элементов в iframe: {len(all_elements)}")
        
        if len(all_elements) > 0:
            print("\n📋 Первые 5 элементов:")
            for i, el in enumerate(all_elements[:5]):
                print(f"  {i+1}. Тег: {el.tag_name}, классы: {el.get_attribute('class')}")
        
        # Проверяем, есть ли текст "подождите"
        body_text = bot.driver.find_element(By.TAG_NAME, "body").text
        print(f"\n📝 Текст в body: {body_text[:200]}")
        
        if "подождите" in body_text.lower():
            print("\n⚠️ ВНИМАНИЕ: iframe ещё не загрузился! Нужно подождать дольше.")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    input("Нажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_iframe_content()