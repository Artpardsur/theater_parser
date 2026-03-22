"""
Тест для проверки доступных мест в Вишневом саду
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from src.parser.edge_bot import EdgeTheaterBot


def find_any_free_seats(driver, max_seats_to_find=10):
    """
    Найти любые свободные места в зале
    
    Returns:
        список свободных мест [{'row': row, 'seat': seat}, ...]
    """
    print("\n🔍 Ищу свободные места...")
    
    # Пробуем разные селекторы для мест
    seat_selectors = [
        "[data-row][data-place]",
        "[data-row][data-seat]",
        "[data-row][data-col]",
        ".seat[data-row]",
        ".place[data-row]",
        "[data-row]"
    ]
    
    free_seats = []
    seen = set()
    
    for selector in seat_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"  Пробую селектор '{selector}': найдено {len(elements)} элементов")
            
            for el in elements:
                try:
                    # Получаем ряд и место
                    row = el.get_attribute("data-row")
                    if not row:
                        row = el.get_attribute("row")
                    
                    place = el.get_attribute("data-place")
                    if not place:
                        place = el.get_attribute("data-col")
                    if not place:
                        place = el.get_attribute("data-seat")
                    if not place:
                        place = el.get_attribute("seat")
                    
                    if row and place:
                        key = f"{row}_{place}"
                        if key in seen:
                            continue
                        seen.add(key)
                        
                        # Проверяем, свободно ли место
                        classes = el.get_attribute("class") or ""
                        is_free = "busy" not in classes and "taken" not in classes and "reserved" not in classes
                        
                        if is_free:
                            free_seats.append({
                                'row': int(row),
                                'seat': int(place),
                                'element': el
                            })
                            
                            if len(free_seats) >= max_seats_to_find:
                                return free_seats
                except:
                    continue
                    
        except Exception as e:
            print(f"  Ошибка с селектором {selector}: {e}")
            continue
    
    return free_seats


def test_vishneviy_sad():
    """Тест для Вишневого сада"""
    print("🎭 ТЕСТ: ВИШНЕВЫЙ САД - ПОИСК СВОБОДНЫХ МЕСТ")
    print("=" * 60)
    
    bot = EdgeTheaterBot(headless=False)
    driver = bot.driver
    
    try:
        # ID Вишневого сада
        session_id = 838
        
        print(f"\n📂 Открываю спектакль: Вишневый сад (ID: {session_id})")
        bot.open_play_page(session_id)
        
        print("🔄 Переключаюсь в схему зала...")
        if not bot.switch_to_hall_iframe():
            print("❌ Не удалось загрузить схему зала")
            return
        
        time.sleep(2)
        
        # Ищем свободные места
        free_seats = find_any_free_seats(driver, max_seats_to_find=20)
        
        print("\n" + "=" * 60)
        print(f"📊 РЕЗУЛЬТАТЫ ПОИСКА:")
        print("=" * 60)
        
        if free_seats:
            print(f"\n✅ Найдено свободных мест: {len(free_seats)}")
            
            # Группируем по рядам
            seats_by_row = {}
            for seat in free_seats:
                row = seat['row']
                if row not in seats_by_row:
                    seats_by_row[row] = []
                seats_by_row[row].append(seat['seat'])
            
            print("\n📋 Свободные места по рядам:")
            print("-" * 40)
            
            for row in sorted(seats_by_row.keys()):
                seats = sorted(seats_by_row[row])
                print(f"  Ряд {row}: места {seats}")
            
            # Предлагаем выбрать места для теста
            print("\n" + "=" * 60)
            print("💡 Для теста выберите любые 2 места из списка выше")
            print("   Затем мы можем проверить, как бот их выбирает")
            
            # Спрашиваем, хочет ли пользователь протестировать выбор мест
            test_choice = input("\nХотите протестировать выбор мест? (да/нет): ").strip().lower()
            
            if test_choice in ['да', 'yes', 'y', 'д']:
                print("\n📝 Введите места для теста (например: 5,1 или 5,1 и 5,2)")
                seat_input = input("Места (ряд,место через пробел): ").strip()
                
                test_seats = []
                for part in seat_input.split():
                    if ',' in part:
                        r, s = part.split(',')
                        test_seats.append({'row': int(r), 'seat': int(s)})
                
                if test_seats:
                    print(f"\n🔍 Пробую выбрать места: {test_seats}")
                    
                    # Пробуем выбрать места
                    selected = bot.select_seats(test_seats)
                    
                    if selected > 0:
                        print(f"\n✅ Выбрано {selected} мест")
                        
                        # Спрашиваем, бронировать ли
                        book_choice = input("\nЗабронировать выбранные места? (да/нет): ").strip().lower()
                        if book_choice in ['да', 'yes', 'y', 'д']:
                            if bot.book_tickets():
                                payment_url = bot.get_payment_url()
                                if payment_url:
                                    print(f"\n🎉 УСПЕХ! Ссылка на оплату: {payment_url}")
                                else:
                                    print("\n❌ Не удалось получить ссылку на оплату")
                            else:
                                print("\n❌ Не удалось забронировать")
                    else:
                        print("\n❌ Не удалось выбрать места")
            
        else:
            print("\n❌ Свободных мест не найдено!")
            print("Возможно, все билеты проданы или спектакль уже прошёл")
            
            # Показываем пример HTML для отладки
            print("\n🔍 Для отладки, ищу любые элементы с атрибутами мест...")
            all_with_data = driver.find_elements(By.CSS_SELECTOR, "[data-row], [data-place]")
            if all_with_data:
                print(f"Найдено элементов с data-row/data-place: {len(all_with_data)}")
                print("Пример первых 3:")
                for i, el in enumerate(all_with_data[:3]):
                    html = el.get_attribute("outerHTML")[:200]
                    print(f"  {i+1}. {html}")
            else:
                print("Элементы с data-row не найдены")
                
                # Пробуем найти любые элементы внутри iframe
                body = driver.find_element(By.TAG_NAME, "body")
                print(f"Содержимое body: {body.get_attribute('innerHTML')[:500]}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    input("\n\nНажмите Enter, чтобы закрыть браузер...")
    bot.close()


if __name__ == "__main__":
    test_vishneviy_sad()