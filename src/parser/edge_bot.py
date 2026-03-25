"""
Театральный парсер для Microsoft Edge
"""

import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EdgeTheaterBot:
    """
    Бот для автоматического бронирования билетов (Microsoft Edge)
    """
    
    def __init__(self, headless=False, minimized=False):
        """
        Инициализация бота
        
        Args:
            headless: если True, браузер будет невидимым (НЕ РЕКОМЕНДУЕТСЯ)
            minimized: если True, браузер будет свернут
        """
        logger.info("Инициализация бота для Microsoft Edge")
        
        # Сохраняем параметры
        self.headless = headless
        self.minimized = minimized
        
        # Настройки Edge
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        # Отключаем автоматизацию
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Создаем драйвер
        driver_path = r"C:\Users\home\Desktop\programs\theater_parser\msedgedriver.exe"
        
        if not os.path.exists(driver_path):
            logger.error(f"Драйвер не найден: {driver_path}")
            raise FileNotFoundError(f"EdgeDriver не найден: {driver_path}")
        
        service = Service(driver_path)
        self.driver = webdriver.Edge(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Скрываем автоматизацию
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Если нужно свернуть окно
        if minimized and not headless:
            self.driver.minimize_window()
            logger.info("Браузер свернут")
        
        logger.info(f"Бот инициализирован (headless={headless}, minimized={minimized})")
    
    def open_play_page(self, session_id):
        """
        Открыть страницу спектакля по ID
        
        Args:
            session_id: ID спектакля (число)
        """
        url = f"https://quicktickets.ru/stavropol-teatr-dramy-lermontova/s{session_id}"
        
        logger.info(f"Открываю страницу: {url}")
        self.driver.get(url)
        time.sleep(3)
        
        if "404" in self.driver.title:
            logger.error("Страница не найдена!")
            return False
        
        logger.info(f"Страница загружена: {self.driver.title}")
        return True
    
    def switch_to_hall_iframe(self):
        """Переключиться в iframe со схемой зала"""
        logger.info("Ищу iframe со схемой зала...")
        
        try:
            iframe = self.wait.until(
                EC.presence_of_element_located((By.NAME, "qt_hall"))
            )
            self.driver.switch_to.frame(iframe)
            logger.info("✅ Переключился в iframe зала")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Не удалось найти iframe: {e}")
            return False
    
    def find_seat_selector(self, row, seat):
        """Найти селектор для места"""
        selectors = [
            f'[data-row="{row}"][data-place="{seat}"]',
            f'[data-row="{row}"][data-seat="{seat}"]',
            f'[data-row="{row}"][data-col="{seat}"]',
            f'[data-row="{row}"][data-number="{seat}"]',
            f'.seat[data-row="{row}"][data-place="{seat}"]',
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    return selector
            except:
                continue
        return None
    
    def select_seats_smart(self, seats_config):
        """
        Выбор мест через поиск по классам (работает внутри iframe)
        """
        logger.info(f"Выбираю места: {seats_config}")
        
        seats_needed = seats_config.get('seats_per_side', 2)
        
        # Ждём, пока загрузятся места
        time.sleep(1)
        
        # Ищем все свободные места
        free_seats = self.driver.find_elements(By.CSS_SELECTOR, ".hallPlace.free")
        logger.info(f"Найдено свободных мест: {len(free_seats)}")
        
        if not free_seats:
            logger.error("Нет свободных мест!")
            return []
        
        # Собираем информацию о местах
        seats_info = []
        for seat in free_seats:
            try:
                # Получаем номер места
                seat_number = ""
                try:
                    number_span = seat.find_element(By.CSS_SELECTOR, ".place_text_only")
                    seat_number = number_span.text.strip()
                except:
                    pass
                
                if not seat_number:
                    seat_number = seat.text.strip()
                
                # Получаем координаты
                style = seat.get_attribute("style")
                left = 0
                top = 0
                if style and "left:" in style:
                    try:
                        left = int(style.split("left:")[1].split("px")[0])
                    except:
                        pass
                if style and "top:" in style:
                    try:
                        top = int(style.split("top:")[1].split("px")[0])
                    except:
                        pass
                
                seats_info.append({
                    'element': seat,
                    'number': seat_number,
                    'left': left,
                    'top': top
                })
                logger.info(f"  Место: №{seat_number}, позиция: ({left}, {top})")
            except Exception as e:
                logger.error(f"Ошибка при чтении места: {e}")
        
        # Сортируем по позиции (слева направо, сверху вниз)
        seats_info.sort(key=lambda x: (x['top'], x['left']))
        
        # Берём первые N мест
        selected = seats_info[:seats_needed]
        
        # Выбираем места: сначала наводим мышь, потом кликаем
        actions = ActionChains(self.driver)
        
        for seat in selected:
            try:
                # Скроллим к месту
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", seat['element'])
                time.sleep(0.5)
                
                # Наводим мышь
                actions.move_to_element(seat['element']).perform()
                time.sleep(0.5)
                
                # Кликаем
                seat['element'].click()
                logger.info(f"✅ Выбрано место №{seat['number']}")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Ошибка при выборе места: {e}")
        
        return [{'number': s['number']} for s in selected]
    
    def select_seats(self, seats):
        """Выбрать конкретные места (простая версия)"""
        logger.info(f"Выбираю конкретные места: {seats}")
        
        selected_count = 0
        
        for seat in seats:
            row = seat['row']
            place = seat['seat']
            
            try:
                selector = self.find_seat_selector(row, place)
                
                if selector:
                    seat_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    classes = seat_element.get_attribute("class") or ""
                    if "busy" in classes or "taken" in classes:
                        logger.warning(f"Место {row}-{place} уже занято")
                        continue
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", seat_element)
                    time.sleep(0.3)
                    seat_element.click()
                    logger.info(f"✅ Выбрано место: ряд {row}, место {place}")
                    selected_count += 1
                    time.sleep(0.3)
                else:
                    logger.warning(f"❌ Место не найдено: ряд {row}, место {place}")
                    
            except Exception as e:
                logger.error(f"Ошибка при выборе места {row}-{place}: {e}")
        
        logger.info(f"Выбрано {selected_count} из {len(seats)} мест")
        return selected_count
    
    def book_tickets(self):
        """Нажать кнопку бронирования (появляется после выбора мест)"""
        logger.info("Нажимаю кнопку бронирования...")
        
        # Убеждаемся, что мы внутри iframe
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".hallPlace")
            logger.info("  Уже внутри iframe")
        except:
            logger.info("  Переключаюсь в iframe")
            self.switch_to_hall_iframe()
        
        # Ждём появления кнопки
        logger.info("  Жду появления кнопки...")
        time.sleep(2)
        
        # Ищем кнопку внутри iframe
        try:
            selectors = [
                "button.button.buy",
                "button.buy",
                ".button.buy",
                "div.buttonGroup button",
                ".buttonGroup button"
            ]
            
            actions = ActionChains(self.driver)
            
            for selector in selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            # Исключаем служебные кнопки
                            classes = button.get_attribute("class") or ""
                            if "showAll" not in classes and "hideAll" not in classes:
                                # Скроллим к кнопке
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                time.sleep(0.5)
                                
                                # Наводим мышь на кнопку
                                actions.move_to_element(button).perform()
                                time.sleep(0.5)
                                
                                # Кликаем
                                button.click()
                                logger.info(f"✅ Кнопка бронирования нажата (селектор: {selector})")
                                time.sleep(3)
                                return True
                except:
                    continue
            
            logger.error("Кнопка бронирования не найдена")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при нажатии кнопки: {e}")
            return False
    
    def get_payment_url(self):
        """Получить URL для оплаты"""
        time.sleep(2)
        current_url = self.driver.current_url
        
        logger.info(f"Текущий URL: {current_url}")
        
        # Проверяем, перешли ли на страницу оплаты
        if "order" in current_url or "payment" in current_url or "anytickets" in current_url:
            logger.info(f"✅ URL для оплаты: {current_url}")
            return current_url
        
        # Если нет, проверяем, нет ли ссылки на странице
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='order'], a[href*='payment']")
            for link in links:
                href = link.get_attribute("href")
                if href and ("order" in href or "payment" in href):
                    logger.info(f"✅ Найдена ссылка на оплату: {href}")
                    return href
        except:
            pass
        
        return None
    
    def find_plays(self, play_name="Вишневый сад"):
        """
        Найти все спектакли с указанным названием на афише
        Использует умный пошаговый скроллинг для загрузки всех карточек
        """
        logger.info(f"Поиск спектаклей '{play_name}' на афише с умным скроллингом")
        
        found_plays = []
        seen_names = set()
        seen_positions = set()
        
        try:
            # Открываем афишу
            url = "https://stavteatr.ru/p/playbill"
            logger.info(f"Открываю афишу: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Получаем размер окна
            window_size = self.driver.get_window_size()
            screen_height = window_size['height']
            
            current_y = 0
            no_new_cards_count = 0
            max_no_new = 5
            max_attempts = 40
            
            logger.info("Начинаю умный сбор спектаклей...")
            
            # Сначала скроллим вверх
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            for attempt in range(max_attempts):
                # Получаем все карточки
                all_cards = self.driver.find_elements(By.CSS_SELECTOR, ".uk-card")
                visible_cards = []
                
                for card in all_cards:
                    try:
                        # Проверяем, видна ли карточка
                        is_visible = self.driver.execute_script(
                            "var elem = arguments[0]; var rect = elem.getBoundingClientRect(); "
                            "return rect.top < window.innerHeight && rect.bottom > 0 && rect.width > 0 && rect.height > 0;",
                            card
                        )
                        
                        if is_visible:
                            # Получаем позицию
                            y_position = self.driver.execute_script(
                                "return arguments[0].getBoundingClientRect().top + window.pageYOffset;",
                                card
                            )
                            
                            # Получаем название
                            name = ""
                            try:
                                name_elem = card.find_element(By.CSS_SELECTOR, "h2.uk-heading-small")
                                name = name_elem.text.strip().strip('"')
                            except:
                                pass
                            
                            # Получаем ссылку
                            link = ""
                            try:
                                link_elem = card.find_element(By.CSS_SELECTOR, "a[data-href]")
                                link = link_elem.get_attribute("data-href")
                            except:
                                pass
                            
                            visible_cards.append({
                                'y_position': y_position,
                                'name': name,
                                'link': link
                            })
                    except:
                        continue
                
                new_cards = 0
                for card in visible_cards:
                    if card['y_position'] in seen_positions:
                        continue
                    
                    seen_positions.add(card['y_position'])
                    
                    if card['name'] and card['name'] not in seen_names:
                        seen_names.add(card['name'])
                        new_cards += 1
                        
                        # Проверяем, подходит ли название
                        if play_name.lower() in card['name'].lower():
                            logger.info(f"Найден спектакль: {card['name']}")
                            
                            # Извлекаем ID из ссылки
                            session_id = None
                            if card['link'] and '/s' in card['link']:
                                match = re.search(r'/s(\d+)', card['link'])
                                if match:
                                    session_id = int(match.group(1))
                            
                            # Получаем дату
                            date_text = ""
                            try:
                                date_elem = card['element'].find_element(By.CSS_SELECTOR, "p.uk-text-primary") if 'element' in card else None
                            except:
                                pass
                            
                            found_plays.append({
                                'id': session_id,
                                'name': card['name'],
                                'date': date_text,
                                'link': card['link']
                            })
                
                if new_cards == 0:
                    no_new_cards_count += 1
                    logger.debug(f"Новых карточек не найдено ({no_new_cards_count}/{max_no_new})")
                else:
                    no_new_cards_count = 0
                
                if no_new_cards_count >= max_no_new:
                    logger.info("Достигнут конец списка")
                    break
                
                # Проверяем конец страницы
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                if current_y + screen_height >= scroll_height - 100:
                    logger.info("Достигнут конец страницы")
                    break
                
                # Скроллим к следующему экрану
                current_y = current_y + screen_height - 50
                self.driver.execute_script(f"window.scrollTo(0, {current_y});")
                time.sleep(0.8)
            
            logger.info(f"Всего найдено спектаклей '{play_name}': {len(found_plays)}")
            
        except Exception as e:
            logger.error(f"Ошибка при поиске спектаклей: {e}")
        
        return found_plays
    
    def is_date_ignored(self, date_str: str) -> bool:
        """Проверить, не игнорируется ли дата"""
        ignored_dates = [
            "19 апреля",
            "20 апреля",
        ]
        
        date_lower = date_str.lower()
        for ignored in ignored_dates:
            if ignored.lower() in date_lower:
                logger.info(f"Дата '{date_str}' в списке игнорируемых")
                return True
        
        return False
    
    def run_auto(self, play_name="Вишневый сад", seats_config=None):
        """
        Автоматический поиск и бронирование по всем датам
        """
        if seats_config is None:
            seats_config = {
                'preferred_rows': [5, 6, 7],
                'seats_per_side': 2
            }
        
        logger.info(f"Начинаю автоматический поиск спектакля '{play_name}'")
        
        try:
            # 1. Находим все спектакли с умным скроллингом
            plays = self.find_plays(play_name)
            
            if not plays:
                logger.warning(f"Спектакли '{play_name}' не найдены")
                return None
            
            logger.info(f"Найдено {len(plays)} спектаклей '{play_name}'")
            
            # 2. Проверяем каждый
            for play in plays:
                play_id = play['id']
                play_date = play.get('date', '')
                
                logger.info(f"Проверяю: {play['name']} (ID: {play_id}) - {play_date}")
                
                # 3. Пропускаем игнорируемые даты
                if self.is_date_ignored(play_date):
                    logger.info(f"  ⏭️ Дата {play_date} игнорируется")
                    continue
                
                # 4. Открываем страницу спектакля
                if not self.open_play_page(play_id):
                    logger.warning(f"  Не удалось открыть страницу")
                    continue
                
                # 5. Переключаемся в iframe
                if not self.switch_to_hall_iframe():
                    logger.warning(f"  Не удалось загрузить схему зала")
                    continue
                
                # 🎯 Отдаляем карту, чтобы увидеть все места
                self.zoom_out(times=2)
                
                # 6. Ищем свободные места
                logger.info(f"  Ищу свободные места...")
                free_seats = self.driver.find_elements(By.CSS_SELECTOR, ".hallPlace.free")
                logger.info(f"  Найдено свободных мест: {len(free_seats)}")
                
                seats_needed = seats_config.get('seats_per_side', 2)
                
                if len(free_seats) >= seats_needed:
                    logger.info(f"  ✅ Найдено достаточно мест!")
                    
                    # Сохраняем выбранные места
                    selected_seats = []
                    for seat in free_seats[:seats_needed]:
                        try:
                            number_span = seat.find_element(By.CSS_SELECTOR, ".place_text_only")
                            seat_number = number_span.text.strip()
                        except:
                            seat_number = ""
                        
                        selected_seats.append({
                            'element': seat,
                            'number': seat_number
                        })
                        logger.info(f"    Место: №{seat_number if seat_number else '?'}")
                    
                    # Делаем браузер видимым (разворачиваем окно)
                    self.make_visible()
                    
                    # Ждём стабилизации
                    time.sleep(1)
                    
                    # 🎯 Ещё раз отдаляем карту (теперь в видимом режиме)
                    self.zoom_out(times=2)
                    
                    # Выбираем места (остаёмся в iframe)
                    logger.info(f"  Выбираю места в видимом режиме...")
                    for seat in selected_seats:
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", seat['element'])
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", seat['element'])
                            logger.info(f"  ✅ Выбрано место №{seat['number']}")
                            time.sleep(0.5)
                        except Exception as e:
                            logger.error(f"  Ошибка при выборе места: {e}")
                    
                    # Даём время, чтобы кнопка стала активной
                    logger.info("  Ожидаю появления кнопки...")
                    time.sleep(2)
                    
                    # Бронируем (остаёмся в iframe!)
                    if self.book_tickets():
                        time.sleep(3)
                        payment_url = self.get_payment_url()
                        if payment_url:
                            logger.info(f"🎉 УСПЕХ! Спектакль {play['name']} {play_date}")
                            return payment_url
                        else:
                            current_url = self.driver.current_url
                            if "order" in current_url or "payment" in current_url:
                                logger.info(f"🎉 УСПЕХ! Страница оплаты: {current_url}")
                                return current_url
                    else:
                        logger.warning(f"  Не удалось забронировать")
                else:
                    logger.info(f"  ❌ Недостаточно свободных мест (нужно {seats_needed}, найдено {len(free_seats)})")
                
                # Возвращаемся на главную страницу для следующей проверки
                self.driver.get("https://stavteatr.ru/p/playbill")
                time.sleep(2)
            
            logger.info("Все спектакли проверены, билетов не найдено")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка в автоматическом поиске: {e}")
            return None
    
    def run(self, session_id, seats=None):
        """Запустить бронирование по конкретному ID"""
        if seats is None:
            seats = [{'row': 5, 'seat': 1}, {'row': 5, 'seat': 2}]
        
        try:
            if not self.open_play_page(session_id):
                return None
            if not self.switch_to_hall_iframe():
                return None
            if self.select_seats(seats) == 0:
                logger.error("Не удалось выбрать места")
                return None
            if not self.book_tickets():
                return None
            return self.get_payment_url()
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return None
    
    def close(self):
        """Закрыть браузер"""
        self.driver.quit()
        logger.info("Браузер закрыт")

    def make_visible(self):
        """Сделать браузер видимым (развернуть окно)"""
        logger.info("Разворачиваю окно браузера...")
        try:
            self.driver.maximize_window()
            logger.info("✅ Окно браузера развернуто")
        except Exception as e:
            logger.error(f"Не удалось развернуть окно: {e}")

    def zoom_out(self, times=2):
        """Отдалить карту (нажать на кнопку минуса)"""
        logger.info(f"Отдаляю карту ({times} раз)...")
        
        # Убеждаемся, что мы внутри iframe
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".hallPlace")
        except:
            self.switch_to_hall_iframe()
        
        time.sleep(0.5)
        
        for i in range(times):
            try:
                # Ищем кнопку минуса
                minus_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".minus, .button.minus, [class*='minus']")
                for btn in minus_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", btn)
                        logger.info(f"  ✅ Нажата кнопка минуса ({i+1}/{times})")
                        time.sleep(0.5)
                        break
            except Exception as e:
                logger.error(f"Ошибка при отдалении: {e}")