"""
Тестовый скрипт для поиска спектаклей с умным скроллингом
"""

import sys
import os
import time
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser.edge_bot import EdgeTheaterBot


def get_visible_cards(driver):
    """
    Получить все видимые карточки спектаклей с их позициями
    
    Returns:
        list of dict: [{'element': element, 'y_position': y, 'name': name}, ...]
    """
    all_cards = driver.find_elements(By.CSS_SELECTOR, ".uk-card")
    visible_cards = []
    
    for card in all_cards:
        try:
            # Проверяем, видна ли карточка на экране
            is_visible = driver.execute_script(
                "var elem = arguments[0]; var rect = elem.getBoundingClientRect(); "
                "return rect.top < window.innerHeight && rect.bottom > 0 && rect.width > 0 && rect.height > 0;",
                card
            )
            
            if is_visible:
                # Получаем позицию карточки
                y_position = driver.execute_script(
                    "return arguments[0].getBoundingClientRect().top + window.pageYOffset;",
                    card
                )
                
                # Пробуем получить название
                name = ""
                try:
                    name_elem = card.find_element(By.CSS_SELECTOR, "h2.uk-heading-small")
                    name = name_elem.text.strip().strip('"')
                except:
                    pass
                
                # Пробуем получить ссылку на билеты
                link = ""
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, "a[data-href]")
                    link = link_elem.get_attribute("data-href")
                except:
                    pass
                
                visible_cards.append({
                    'element': card,
                    'y_position': y_position,
                    'name': name,
                    'link': link
                })
        except:
            continue
    
    return visible_cards


def scroll_to_next_screen(driver, current_y, screen_height):
    """
    Прокрутить до следующего экрана, избегая перекрытия
    
    Returns:
        float: новая позиция скролла
    """
    # Скроллим на высоту экрана минус небольшой отступ
    new_y = current_y + screen_height - 50
    driver.execute_script(f"window.scrollTo(0, {new_y});")
    time.sleep(0.8)
    return new_y


def collect_all_plays(driver, max_attempts=30):
    """
    Собрать все спектакли с помощью умного скроллинга
    
    Returns:
        list of dict: [{'name': name, 'link': link, 'y_position': y}, ...]
    """
    print("\n📋 Начинаю сбор спектаклей...")
    print("-" * 50)
    
    all_plays = []
    seen_names = set()  # Для избежания дубликатов
    seen_positions = set()  # Для отслеживания позиций
    
    # Получаем размер окна
    window_size = driver.get_window_size()
    screen_height = window_size['height']
    
    # Начальная позиция
    current_y = 0
    no_new_cards_count = 0
    max_no_new = 5  # Если 5 раз подряд нет новых карточек, останавливаемся
    
    # Сначала скроллим вверх, чтобы начать с начала
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    
    for attempt in range(max_attempts):
        # Получаем видимые карточки
        visible_cards = get_visible_cards(driver)
        
        new_cards_found = 0
        
        for card in visible_cards:
            # Проверяем, не видели ли мы уже эту карточку
            if card['y_position'] in seen_positions:
                continue
            
            # Проверяем, не видели ли мы уже такое название
            if card['name'] and card['name'] in seen_names:
                continue
            
            seen_positions.add(card['y_position'])
            
            if card['name']:
                seen_names.add(card['name'])
                new_cards_found += 1
                all_plays.append({
                    'name': card['name'],
                    'link': card['link'],
                    'y_position': card['y_position']
                })
                print(f"  📌 Найден: {card['name']}")
        
        if new_cards_found == 0:
            no_new_cards_count += 1
            print(f"  ⏳ Новых карточек не найдено ({no_new_cards_count}/{max_no_new})")
        else:
            no_new_cards_count = 0
        
        # Проверяем, не пора ли остановиться
        if no_new_cards_count >= max_no_new:
            print("  🛑 Достигнут конец списка")
            break
        
        # Проверяем, не достигли ли конца страницы
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if current_y + screen_height >= scroll_height - 100:
            print("  📍 Достигнут конец страницы")
            break
        
        # Скроллим к следующему экрану
        current_y = scroll_to_next_screen(driver, current_y, screen_height)
    
    return all_plays


def find_and_scroll_to_play(driver, play_name, all_plays):
    """
    Найти спектакль по названию и прокрутить к нему
    
    Args:
        driver: веб-драйвер
        play_name: название спектакля
        all_plays: список всех найденных спектаклей
    
    Returns:
        dict: информация о спектакле или None
    """
    # Ищем спектакль
    target_play = None
    for play in all_plays:
        if play_name.lower() in play['name'].lower():
            target_play = play
            break
    
    if not target_play:
        print(f"❌ Спектакль '{play_name}' не найден")
        return None
    
    print(f"\n✅ Найден спектакль: {target_play['name']}")
    print(f"   Позиция: {target_play['y_position']}px")
    
    if target_play.get('link'):
        session_id = target_play['link'].split('/s')[-1].split('?')[0] if '/s' in target_play['link'] else None
        if session_id:
            print(f"   ID спектакля: {session_id}")
            print(f"   Ссылка: https://quicktickets.ru/stavropol-teatr-dramy-lermontova/s{session_id}")
    
    # Скроллим к спектаклю
    driver.execute_script(f"window.scrollTo(0, {target_play['y_position'] - 100});")
    time.sleep(1)
    
    print(f"\n✅ Прокрутил к: {target_play['name']}")
    
    return target_play


def test_find():
    """Тестируем поиск спектаклей"""
    print("🎭 ТЕАТРАЛЬНЫЙ ПАРСЕР - ПОИСК СПЕКТАКЛЕЙ")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    driver = bot.driver
    
    # Открываем афишу
    print("\n📂 Открываю афишу...")
    driver.get("https://stavteatr.ru/p/playbill")
    time.sleep(3)
    
    # Собираем все спектакли
    all_plays = collect_all_plays(driver)
    
    # Выводим результаты
    print("\n" + "=" * 60)
    print(f"📊 ВСЕГО НАЙДЕНО СПЕКТАКЛЕЙ: {len(all_plays)}")
    print("=" * 60)
    
    for i, play in enumerate(all_plays, 1):
        print(f"{i:3}. {play['name']}")
    
    print("=" * 60)
    
    # Ищем нужные спектакли
    search_terms = ["Крыша", "Вишневый", "Доходное место", "Концерт"]
    
    print("\n🔍 РЕЗУЛЬТАТЫ ПОИСКА:")
    print("-" * 40)
    
    for term in search_terms:
        found = [play for play in all_plays if term.lower() in play['name'].lower()]
        if found:
            print(f"\n✅ '{term}':")
            for play in found:
                print(f"   🎭 {play['name']}")
                if play['link']:
                    print(f"      🔗 ID: {play['link'].split('/s')[-1] if '/s' in play['link'] else 'не найден'}")
        else:
            print(f"\n❌ '{term}' не найден")
    
    # Предлагаем прокрутить к выбранному спектаклю
    print("\n" + "=" * 60)
    target = input("Введите название спектакля для перехода (или Enter для выхода): ").strip()
    
    if target:
        target_play = find_and_scroll_to_play(driver, target, all_plays)
        
        if target_play:
            print(f"\n✅ Прокрутил к: {target_play['name']}")
            print("   Спектакль подсвечен красной рамкой")
            
            if target_play['link']:
                session_id = target_play['link'].split('/s')[-1] if '/s' in target_play['link'] else None
                if session_id:
                    print(f"   ID спектакля: {session_id}")
                    print(f"   Ссылка: https://quicktickets.ru/stavropol-teatr-dramy-lermontova/s{session_id}")
    
    input("\n\n📌 Нажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_find()