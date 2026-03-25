import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains

driver_path = r"C:\Users\home\Desktop\programs\theater_parser\msedgedriver.exe"

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(driver_path)
driver = webdriver.Edge(service=service, options=options)
driver.maximize_window()

try:
    # 1. Открыть страницу
    print("Открываю страницу...")
    driver.get("https://quicktickets.ru/stavropol-teatr-dramy-lermontova/s838")
    time.sleep(3)
    
    # 2. Переключиться в iframe
    print("Переключаюсь в iframe...")
    iframe = driver.find_element(By.NAME, "qt_hall")
    driver.switch_to.frame(iframe)
    time.sleep(2)
    
    # 3. Отдалить карту (нажать минус 2 раза)
    print("Отдаляю карту...")
    for i in range(2):
        minus_buttons = driver.find_elements(By.CSS_SELECTOR, ".minus")
        for btn in minus_buttons:
            if btn.is_displayed():
                btn.click()
                print(f"  Нажата кнопка минуса {i+1}")
                time.sleep(1)
                break
    
    # 4. Найти свободное место
    print("Ищу свободное место...")
    free_seats = driver.find_elements(By.CSS_SELECTOR, ".hallPlace.free")
    print(f"Найдено свободных мест: {len(free_seats)}")
    
    if not free_seats:
        print("Нет свободных мест!")
        driver.quit()
        exit()
    
    first_seat = free_seats[0]
    
    # 5. Навести мышь на место
    print("Навожу мышь на место...")
    actions = ActionChains(driver)
    actions.move_to_element(first_seat).perform()
    time.sleep(1)
    print("Мышь наведена")
    
    # 6. Кликнуть
    print("Кликаю...")
    first_seat.click()
    time.sleep(1)
    print("Клик выполнен")
    
    # 7. Проверяем, выбралось ли место
    print("Проверяю, выбралось ли место...")
    selected = driver.find_elements(By.CSS_SELECTOR, ".hallPlace.selected, .hallPlace.active, .hallPlace.sel, .hallPlace.hovered")
    if selected:
        print(f"✅ Выбрано {len(selected)} мест!")
    else:
        print("❌ Место не выбралось")
        # Пробуем клик через JavaScript
        print("Пробую JavaScript клик...")
        driver.execute_script("arguments[0].click();", first_seat)
        time.sleep(1)
        
        selected = driver.find_elements(By.CSS_SELECTOR, ".hallPlace.selected, .hallPlace.active")
        if selected:
            print(f"✅ Выбрано {len(selected)} мест!")
    
    # 8. Ждать появления кнопки
    print("Жду появления кнопки...")
    time.sleep(2)
    
    # 9. Искать кнопку Купить
    print("Ищу кнопку Купить...")
    buy_buttons = driver.find_elements(By.CSS_SELECTOR, "button.buy, .button.buy")
    if buy_buttons:
        print(f"Найдено кнопок: {len(buy_buttons)}")
        for btn in buy_buttons:
            if btn.is_displayed():
                print("Кнопка видима!")
                btn.click()
                print("Кнопка нажата!")
                time.sleep(2)
                print(f"Текущий URL: {driver.current_url}")
    else:
        print("Кнопка не найдена!")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print("Все кнопки в iframe:")
        for i, btn in enumerate(all_buttons):
            print(f"  {i+1}. классы: {btn.get_attribute('class')}, текст: '{btn.text}'")
    
    input("\nНажмите Enter для выхода...")
    
finally:
    driver.quit()