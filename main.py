import pyautogui
import keyboard
import pyttsx3
import time
import pytesseract
from PIL import Image
import traceback
import os
import re
from datetime import datetime

# Конфигурация
CONFIG_FILE = 'setting.txt'
LOG_FILE = 'log.txt'
SCREENSHOT_FILE = 'dialog_screenshot.png'
LAST_DIALOG_FILE = 'last_dialog.txt'
TESSERACT_PATH = r"Tesseract-OCR\tesseract.exe"

class DialogReader:
    def __init__(self):
        self.load_settings()
        self.setup_tts()
        self.running = True
        
    def load_settings(self):
        # Значения по умолчанию
        self.screen_width = 1920
        self.screen_height = 1080
        self.use_count = 0
        self.activation_key = 't'
        self.delay_before_capture = 1.5
        self.voice_name = 'Microsoft Irina Desktop'
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                settings = f.read().split('\n')
                if len(settings) >= 2:
                    self.screen_width = int(settings[0])
                    self.screen_height = int(settings[1])
                if len(settings) >= 3:
                    self.use_count = int(settings[2])
                if len(settings) >= 4 and settings[3].strip():
                    self.delay_before_capture = float(settings[3])
                if len(settings) >= 5 and settings[4].strip():
                    self.voice_name = settings[4].strip()
        except (FileNotFoundError, ValueError) as e:
            self.log_event(f"Ошибка загрузки настроек: {str(e)}", True)
            self.save_settings()

    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f:
            f.write(f"{self.screen_width}\n{self.screen_height}\n{self.use_count}\n{self.delay_before_capture}\n{self.voice_name}")

    def setup_tts(self):
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Скорость речи
        
        # Установка выбранного голоса
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if self.voice_name in voice.name:
                self.tts_engine.setProperty('voice', voice.id)
                break
        else:
            # Если выбранный голос не найден, используем первый русский
            for voice in voices:
                if 'russian' in voice.languages or 'ru' in voice.languages:
                    self.tts_engine.setProperty('voice', voice.id)
                    break

    def capture_dialog_area(self):
        """Захватывает область, где обычно появляется диалог (правая половина экрана)"""
        region = (
            int(self.screen_width / 2),  # x-start
            0,                           # y-start
            int(self.screen_width / 2),  # width
            int(self.screen_height * 0.3) # height (верхняя часть)
        )
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(SCREENSHOT_FILE)
        return SCREENSHOT_FILE

    def extract_text_from_image(self, image_path):
        """Извлекает текст из изображения с предварительной обработкой"""
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        
        # Предварительная обработка изображения
        img = Image.open(image_path)
        img = img.convert('L')  # В градации серого
        img = img.point(lambda x: 0 if x < 140 else 255)  # Бинаризация
        
        # Распознавание с указанием русского языка
        text = pytesseract.image_to_string(img, lang='rus+eng')
        
        # Очистка текста
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_valid_dialog(self, text):
        """Проверяет, является ли текст валидным диалогом"""
        if not text:
            return False
            
        # Игнорируем короткие тексты (возможно, шум)
        if len(text) < 10:
            return False
            
        # Проверяем наличие признаков диалога
        if '-' in text or ':' in text or '»' in text:
            return True
            
        return False

    def log_event(self, message, is_error=False):
        """Логирование событий"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {'ERROR' if is_error else 'INFO'}: {message}\n"
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        print(log_entry.strip())

    def save_last_dialog(self, text):
        """Сохраняет последний диалог в файл"""
        with open(LAST_DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(text)

    def stop(self):
        """Остановка работы скрипта"""
        self.running = False
        self.log_event("Программа остановлена")

    def run(self):
        self.log_event("Программа запущена")
        self.log_event(f"Настройки: {self.screen_width}x{self.screen_height}, задержка: {self.delay_before_capture} сек")
        self.log_event(f"Выбранный голос: {self.voice_name}")

        try:
            while self.running:
                if keyboard.is_pressed(self.activation_key):
                    try:
                        time.sleep(self.delay_before_capture)
                        
                        # Захват и обработка диалога
                        screenshot_path = self.capture_dialog_area()
                        self.log_event("Скриншот диалога сохранен")
                        
                        text = self.extract_text_from_image(screenshot_path)
                        self.log_event(f"Распознанный текст: {text}")
                        
                        if self.is_valid_dialog(text):
                            self.save_last_dialog(text)
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                            
                            self.use_count += 1
                            self.save_settings()
                        else:
                            self.log_event("Распознанный текст не похож на диалог")
                            
                        # Задержка для предотвращения многократного срабатывания
                        time.sleep(1)
                            
                    except Exception as e:
                        self.log_event(f"Ошибка: {str(e)}\n{traceback.format_exc()}", True)
                        time.sleep(1)
                        
                # Небольшая задержка для снижения нагрузки на CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.stop()

if __name__ == "__main__":
    reader = DialogReader()
    try:
        reader.run()
    except Exception as e:
        reader.log_event(f"Критическая ошибка: {str(e)}\n{traceback.format_exc()}", True)
        reader.stop()