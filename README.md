# Описание
TTS TESO - Text-to-Speech для The Elder Scrolls Online
Программа для автоматического озвучивания диалогов в The Elder Scrolls Online (TESO) с помощью OCR и синтеза речи.

Программа была собрана в exe, не требует дополнительных манипуляций по ссылке(в будущем)

Для репозитория в ГитХаб требуется прочитать описание ниже

# Возможности

-Автоматическое распознавание текста (через Tesseract OCR)

-Озвучивание диалогов (поддержка русских и английских голосов)

-Гибкие настройки:

-Выбор разрешения экрана (HD, Full HD, 2K, 4K)

-Настройка задержки перед захватом текста

-Выбор голоса синтезатора (Microsoft Irina, David, Zira)

-Статистика использования (счётчик, последний распознанный текст)

-Простой интерфейс с тёмной темой


# Установка

Требования:

Python 3.8+ ([скачать](https://www.python.org/downloads/))

Tesseract OCR ([установка](https://github.com/UB-Mannheim/tesseract/wiki))(ВАЖНО!!!
Установите и добавьте в корень программы, с названием папки Tesseract-OCR)

Для Tesseract OCR, потребуется установить базу данных ([ссылка](https://github.com/tesseract-ocr/tessdata/tree/main))

Зависимости:
```
    pip install pyautogui keyboard pyttsx3 pytesseract pillow
```

# Настройка

Выберите разрешение экрана в настройках (по умолчанию 1920×1080).

Укажите задержку перед захватом текста (рекомендуется 1.5 сек).

Выберите голос синтезатора (русский доступен только один, Ирина).

Нажмите T в игре, чтобы программа озвучила диалог.


# Важно
Программа не взаимодействует напрямую с игрой, а только анализирует скриншоты.

Для работы нужен Tesseract OCR (установите в корень программы, с названием папки Tesseract-OCR).

Если голоса не работают, проверьте установку языковых пакетов Windows.

# Приятной игры в TESO! 

# Используемые библиотеки

>tkinter (графический интерфейс)

Для чего: Создание окон, кнопок, выпадающих списков и других элементов интерфейса.

Места в коде:

    Основное окно: ```root = tk.Tk()```
    Создание фреймов (например, ```self.sidebar = tk.Frame(...)```)
    Кнопки (например, ```self.start_button = tk.Button(...)```)
    Методы ```create_home_page(), create_settings_page()``` и др.
___
>ttk (стилизованные виджеты)

Для чего: Улучшенные элементы интерфейса (Combobox, Checkbutton).
Места в коде:
    Выпадающие списки:
```python
self.resolution_menu = ttk.Combobox(...)
```

    Стили:

```python
style = ttk.Style()
style.configure('Custom.TCombobox', ...)
```
___
>pip install pyautogui

Данная библиотека используется для создания скриншота, в определенной области. В коде данная функция используеься в 53 строке:

```python
spyautogui.screenshot('dialog_screenshot.png', region=(x, y, width, height))
``` 

В нашем случае мы делаем скриншот, лишь половины экрана.
___
>pip install keyboard

Данная библиотека используется для прослушивания нажатий клавиатуры. Используется в 51 строке:
```python
if keyboard.is_pressed(self.activation_key):
```
___
>pip install speech_recognition

>pip install pyttsx3

Для чего: Озвучивание распознанного текста.
```python
self.tts_engine = pyttsx3.init()
self.tts_engine.say(text)
self.tts_engine.runAndWait()
```
___
>pip install pytesseract

Для чего: Извлечение текста из скриншотов.
```python
pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe"
text = pytesseract.image_to_string(img, lang='rus+eng')
```
___
>pip install Pillow

Для чего: Преобразование скриншотов для лучшего распознавания.
```python
img = Image.open(image_path)
img = img.convert('L')  # Градации серого
```
___
> import datetime

Для чего: Добавление временных меток в логи ошибок.
```python
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```
___
> import subprocess 

Для чего: Запуск main.py из интерфейса.
```python
self.process = subprocess.Popen(["python", "main.py"])
self.process.terminate()
```
# Обратная связь
Если у вас есть вопросы или предложения:
✉ Email: wwwevowww@gmail.com