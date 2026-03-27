import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

# Путь к драйверу (укажите ваш)
driver_path = r"C:\Users\home\Desktop\programs\theater_parser\msedgedriver.exe"

# Настройки
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(driver_path)
driver = webdriver.Edge(service=service, options=options)
driver.maximize_window()

try:
    # 1. Открыть страницу спектакля
    print("📂 Открываю страницу спектакля...")
    driver.get("https://quicktickets.ru/stavropol-teatr-dramy-lermontova/s838")
    time.sleep(3)

    # 2. Переключиться в iframe со схемой зала
    print("🔄 Переключаюсь в iframe...")
    iframe = driver.find_element(By.NAME, "qt_hall")
    driver.switch_to.frame(iframe)
    time.sleep(2)

    # 3. Найти свободное место (первое попавшееся)
    print("🔍 Ищу свободное место...")
    free_seats = driver.find_elements(By.CSS_SELECTOR, ".hallPlace.free")
    print(f"Найдено свободных мест: {len(free_seats)}")

    if not free_seats:
        print("❌ Нет свободных мест, тест остановлен.")
        input("Нажмите Enter для выхода...")
        driver.quit()
        exit()

    # 4. Выбрать первое свободное место
    first_seat = free_seats[0]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_seat)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", first_seat)
    print("✅ Место выбрано (клик через JS)")

    # 5. Ждать появления кнопки "Купить"
    print("⏳ Жду появления кнопки 'Купить'...")
    time.sleep(2)

    # 6. Ищем кнопку внутри iframe
    buy_button = None
    selectors = ["button.button.buy", "button.buy", ".button.buy"]
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    buy_button = btn
                    break
            if buy_button:
                break
        except:
            continue

    if buy_button:
        print("✅ КНОПКА 'КУПИТЬ' ПОЯВИЛАСЬ!")
        print(f"   Её классы: {buy_button.get_attribute('class')}")
    else:
        print("❌ Кнопка 'Купить' НЕ появилась.")
        print("   Показываю все кнопки в iframe:")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(all_buttons):
            print(f"   {i+1}. классы: {btn.get_attribute('class')}, текст: '{btn.text}'")

    input("\nНажмите Enter, чтобы закрыть браузер...")

finally:
    driver.quit()