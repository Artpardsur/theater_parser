"""
Планировщик для театрального парсера
Запускает main.py каждые 5-10 минут
"""

import time
import random
import subprocess
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем бота для проверки изменений
from src.parser.edge_bot import EdgeTheaterBot


class SimpleScheduler:
    def __init__(self):
        self.bot = None
        self.last_hash = None
        self.check_count = 0
    
    def get_page_hash(self):
        """Получить хэш страницы афиши"""
        try:
            import hashlib
            import requests
            
            url = "https://stavteatr.ru/p/playbill"
            response = requests.get(url, timeout=10)
            return hashlib.md5(response.text.encode()).hexdigest()
        except Exception as e:
            print(f"Ошибка при получении хэша: {e}")
            return None
    
    def run_parser(self):
        """Запустить парсер"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Запускаю парсер...")
        
        try:
            # Запускаем main.py
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                timeout=300  # 5 минут максимум
            )
            
            if result.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Парсер завершил работу")
                if "БИЛЕТЫ НАЙДЕНЫ" in result.stdout:
                    print("🎉🎉🎉 НАЙДЕНЫ БИЛЕТЫ! 🎉🎉🎉")
                    print(result.stdout)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Таймаут парсера")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка: {e}")
    
    def run_with_check(self, use_hash_check=True):
        """
        Запуск с проверкой изменений на странице
        
        Args:
            use_hash_check: если True, проверяем хэш страницы перед запуском
        """
        print("🔄 ПЛАНИРОВЩИК ЗАПУЩЕН")
        print("=" * 60)
        print("Режим: проверка каждые 5-10 минут")
        if use_hash_check:
            print("  + проверка изменений на странице афиши")
        print()
        
        # Получаем начальный хэш
        if use_hash_check:
            self.last_hash = self.get_page_hash()
            if self.last_hash:
                print(f"Начальный хэш страницы: {self.last_hash[:16]}...")
            else:
                print("⚠️ Не удалось получить хэш, запускаю парсер при каждой проверке")
        
        try:
            while True:
                self.check_count += 1
                print(f"\n{'='*60}")
                print(f"📊 ПРОВЕРКА #{self.check_count}")
                print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Проверяем, нужно ли запускать парсер
                should_run = True
                
                if use_hash_check and self.last_hash:
                    current_hash = self.get_page_hash()
                    if current_hash:
                        if current_hash == self.last_hash:
                            print(f"📄 Хэш не изменился ({current_hash[:16]}...)")
                            print("   Пропускаю запуск парсера")
                            should_run = False
                        else:
                            print(f"🔄 Хэш ИЗМЕНИЛСЯ!")
                            print(f"   Было: {self.last_hash[:16]}...")
                            print(f"   Стало: {current_hash[:16]}...")
                            self.last_hash = current_hash
                            should_run = True
                    else:
                        print("⚠️ Не удалось получить хэш, запускаю парсер")
                        should_run = True
                
                if should_run:
                    self.run_parser()
                else:
                    print("⏭️ Пропуск проверки")
                
                # Случайный интервал от 5 до 10 минут (300-600 секунд)
                interval = random.randint(1 * 60, 2 * 60)
                minutes = interval // 60
                seconds = interval % 60
                
                print(f"\n⏰ Следующая проверка через {minutes} мин {seconds} сек...")
                print("   (нажмите Ctrl+C для выхода)")
                
                # Считаем секунды
                for i in range(interval, 0, -1):
                    if i % 60 == 0 and i > 0:
                        mins_left = i // 60
                        print(f"   ⏳ Осталось {mins_left} мин...", end='\r')
                    time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Планировщик остановлен пользователем")


def main():
    """Запуск планировщика"""
    scheduler = SimpleScheduler()
    
    # Выберите режим:
    # scheduler.run_with_check(use_hash_check=True)   # С проверкой хэша (экономит ресурсы)
    scheduler.run_with_check(use_hash_check=False)    # Без проверки (запускает каждые 5-10 мин)


if __name__ == "__main__":
    main()