import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
from datetime import datetime

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS TESO")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Инициализация атрибутов
        self.resolutions = [
            ("1280×720 (HD)", "1280", "720"),
            ("1920×1080 (Full HD)", "1920", "1080"),
            ("2560×1440 (2K)", "2560", "1440"),
            ("3840×2160 (4K)", "3840", "2160")
        ]
        self.delay_options = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        self.default_delay = 1.5
        self.voices = {
            'Microsoft Irina Desktop': 'russian',
            'Microsoft David Desktop': 'english',
            'Microsoft Zira Desktop': 'english'
        }
        self.process = None
        self.animation_running = False
        self.current_page = "main"
        
        # Цветовая схема
        self.bg_color = "#2a2a2a"
        self.sidebar_color = "#1a1a1a"
        self.primary_color = "#FFA726"
        self.secondary_color = "#FFD54F"
        self.text_color = "#ffffff"
        self.card_color = "#333333"
        self.combo_bg = "#3a3a3a"
        self.combo_fg = "#ffffff"
        self.error_color = "#EF5350"
        
        # Тексты интерфейса
        self.texts = {
            "main": "Главная",
            "settings": "Настройки",
            "stats": "Статистика",
            "about": "О программе",
            "title": "Text-to-Speech TESO",
            "start": "СТАРТ",
            "stop": "СТОП",
            "usage": "Счетчик использований:",
            "resolution": "Выберите разрешение:",
            "custom": "Другое разрешение",
            "width": "Ширина:",
            "height": "Высота:",
            "apply": "Применить",
            "delay": "Задержка перед захватом (сек):",
            "voice": "Голос синтезатора:",
            "last_text": "Последний текст:",
            "last_error": "Последняя ошибка:",
            "instructions": "Инструкция:\n1. Выберите язык в Настройках\n2. Установите разрешение экрана\n3. Нажмите СТАРТ для начала",
            "about_text": "О программе: TTS TESO — это программа для автоматического озвучивания \nтекста диалогов в игре The Elder Scrolls Online (TESO). \nОна захватывает текст с экрана, распознаёт \nего с помощью OCR (Tesseract) и воспроизводит\n голосом через синтезатор речи (TTS).\n\nОбратная связь: wwwevowww@gmail.com\n\nВерсия 1.1"
        }
        
        # Создание элементов интерфейса
        self.create_ui()
        
        # Загрузка настроек
        self.load_settings()
        
        # Показать начальную страницу
        self.show_page("main")

    def load_settings(self):
        try:
            with open("setting.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                # Разрешение
                if len(lines) >= 2:
                    width = lines[0].strip()
                    height = lines[1].strip()
                    for res in self.resolutions:
                        if res[1] == width and res[2] == height:
                            self.resolution_var.set(res[0])
                            break
                
                # Задержка
                if len(lines) >= 4:
                    delay = lines[3].strip()
                    if delay and float(delay) in self.delay_options:
                        self.delay_var.set(delay)
                
                # Голос
                if len(lines) >= 5:
                    voice = lines[4].strip()
                    if voice in self.voices:
                        self.voice_var.set(voice)
                        
        except FileNotFoundError:
            # Устанавливаем значения по умолчанию
            self.delay_var.set(str(self.default_delay))
            self.voice_var.set(next(iter(self.voices.keys())))
            self.save_all_settings()

    def create_ui(self):
        # Главный контейнер
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Боковое меню
        self.sidebar = tk.Frame(self.main_container, bg=self.sidebar_color, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Логотип
        self.logo_label = tk.Label(
            self.sidebar, 
            text="TTS TESO", 
            font=("Segoe UI", 18, "bold"), 
            fg=self.primary_color, 
            bg=self.sidebar_color,
            pady=20
        )
        self.logo_label.pack(fill=tk.X)
        
        # Кнопки меню
        self.menu_buttons = []
        menu_items = ["main", "settings", "stats", "about"]
        
        for item in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=self.texts[item],
                font=("Segoe UI", 12),
                fg=self.text_color,
                bg=self.sidebar_color,
                activebackground=self.primary_color,
                activeforeground=self.text_color,
                bd=0,
                padx=20,
                pady=15,
                anchor="w",
                command=lambda t=item: self.switch_page(t)
            )
            btn.pack(fill=tk.X)
            self.menu_buttons.append(btn)
        
        # Основная область контента
        self.content_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок контента
        self.content_header = tk.Frame(self.content_frame, bg=self.bg_color, height=60)
        self.content_header.pack(fill=tk.X)
        
        self.title_label = tk.Label(
            self.content_header, 
            text="", 
            font=("Segoe UI", 20, "bold"), 
            fg=self.text_color, 
            bg=self.bg_color,
            pady=15,
            padx=20
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Создание страниц
        self.pages = {}
        self.create_home_page()
        self.create_settings_page()
        self.create_stats_page()
        self.create_about_page()

    def create_home_page(self):
        page = tk.Frame(self.content_frame, bg=self.bg_color)
        self.pages["main"] = page
        
        # Кнопка Start/Stop
        self.start_button = tk.Button(
            page,
            text=self.texts["start"],
            font=("Segoe UI", 16, "bold"),
            bg=self.primary_color,
            fg="#000000",
            activebackground="#FFCA28",
            activeforeground="#000000",
            bd=0,
            padx=40,
            pady=20,
            command=self.toggle_script
        )
        self.start_button.pack(pady=50)
        
        # Инструкция
        instruction_label = tk.Label(
            page,
            text=self.texts["instructions"],
            font=("Segoe UI", 12),
            fg=self.text_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        instruction_label.pack(pady=20, padx=30, fill=tk.X)

    def create_settings_page(self):
        page = tk.Frame(self.content_frame, bg=self.bg_color)
        self.pages["settings"] = page
        
        # Выбор разрешения
        resolution_frame = tk.Frame(page, bg=self.bg_color)
        resolution_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            resolution_frame, 
            text=self.texts["resolution"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.bg_color
        ).pack(anchor="w", pady=5)
        
        self.resolution_var = tk.StringVar()
        self.resolution_menu = ttk.Combobox(
            resolution_frame,
            textvariable=self.resolution_var,
            values=[res[0] for res in self.resolutions],
            state="readonly",
            font=("Segoe UI", 10),
            style='Custom.TCombobox'
        )
        self.resolution_menu.pack(fill=tk.X, pady=5)
        self.resolution_menu.bind("<<ComboboxSelected>>", self.update_resolution)
        
        # Кастомное разрешение
        self.custom_res_var = tk.BooleanVar()
        custom_check = ttk.Checkbutton(
            resolution_frame,
            text=self.texts["custom"],
            variable=self.custom_res_var,
            command=self.toggle_custom_resolution,
            style='Custom.TCheckbutton'
        )
        custom_check.pack(anchor="w", pady=5)
        
        self.custom_frame = tk.Frame(resolution_frame, bg=self.bg_color)
        
        tk.Label(self.custom_frame, text=self.texts["width"], 
               font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color
        ).grid(row=0, column=0, padx=5)
        
        self.width_entry = ttk.Entry(self.custom_frame, font=("Segoe UI", 10), width=10)
        self.width_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(self.custom_frame, text=self.texts["height"], 
               font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color
        ).grid(row=0, column=2, padx=5)
        
        self.height_entry = ttk.Entry(self.custom_frame, font=("Segoe UI", 10), width=10)
        self.height_entry.grid(row=0, column=3, padx=5)
        
        apply_button = ttk.Button(
            self.custom_frame,
            text=self.texts["apply"],
            command=self.apply_custom_resolution,
            style='Custom.TButton'
        )
        apply_button.grid(row=1, column=0, columnspan=4, pady=10)

        # Настройка задержки
        delay_frame = tk.Frame(page, bg=self.bg_color)
        delay_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            delay_frame, 
            text=self.texts["delay"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.bg_color
        ).pack(anchor="w", pady=5)
        
        self.delay_var = tk.StringVar(value=str(self.default_delay))
        delay_menu = ttk.Combobox(
            delay_frame,
            textvariable=self.delay_var,
            values=self.delay_options,
            state="readonly",
            font=("Segoe UI", 10),
            style='Custom.TCombobox'
        )
        delay_menu.pack(fill=tk.X, pady=5)
        tk.Label(
            delay_frame, 
            text="Рекомендуется: 1.5 сек", 
            font=("Segoe UI", 10), 
            fg=self.secondary_color, 
            bg=self.bg_color
        ).pack(anchor="w")

        # Выбор голоса
        voice_frame = tk.Frame(page, bg=self.bg_color)
        voice_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            voice_frame, 
            text=self.texts["voice"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.bg_color
        ).pack(anchor="w", pady=5)
        
        self.voice_var = tk.StringVar()
        voice_menu = ttk.Combobox(
            voice_frame,
            textvariable=self.voice_var,
            values=list(self.voices.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style='Custom.TCombobox'
        )
        voice_menu.pack(fill=tk.X, pady=5)
        
        # Кнопка сохранения
        save_frame = tk.Frame(page, bg=self.bg_color)
        save_frame.pack(pady=20)
        
        save_btn = ttk.Button(
            save_frame,
            text="Сохранить все настройки",
            command=self.save_all_settings,
            style='Custom.TButton'
        )
        save_btn.pack()

    def create_stats_page(self):
        page = tk.Frame(self.content_frame, bg=self.bg_color)
        self.pages["stats"] = page
        
        # Счетчик использований
        usage_frame = tk.Frame(page, bg=self.card_color, padx=20, pady=10)
        usage_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            usage_frame, 
            text=f"{self.texts['usage']} {self.get_counter()}", 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.card_color
        ).pack(anchor="w")
        
        # Последний текст
        text_frame = tk.Frame(page, bg=self.card_color, padx=20, pady=10)
        text_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            text_frame, 
            text=self.texts["last_text"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.card_color
        ).pack(anchor="w")
        
        last_text = self.get_last_text()
        tk.Label(
            text_frame, 
            text=last_text, 
            font=("Segoe UI", 10), 
            fg=self.secondary_color, 
            bg=self.card_color,
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor="w", pady=5)
        
        # Последняя ошибка
        error_frame = tk.Frame(page, bg=self.card_color, padx=20, pady=10)
        error_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            error_frame, 
            text=self.texts["last_error"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.card_color
        ).pack(anchor="w")
        
        last_error = self.get_last_error()
        tk.Label(
            error_frame, 
            text=last_error, 
            font=("Segoe UI", 10), 
            fg=self.error_color, 
            bg=self.card_color,
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor="w", pady=5)

    def create_about_page(self):
        page = tk.Frame(self.content_frame, bg=self.bg_color)
        self.pages["about"] = page
        
        about_frame = tk.Frame(page, bg=self.card_color, padx=20, pady=20)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            about_frame, 
            text=self.texts["about_text"], 
            font=("Segoe UI", 12), 
            fg=self.text_color, 
            bg=self.card_color,
            justify=tk.LEFT
        ).pack(anchor="w")

    def show_page(self, page_key):
        self.current_page = page_key
        self.title_label.config(text=self.texts[page_key])
        
        # Скрыть текущую страницу
        for page in self.pages.values():
            page.pack_forget()
        
        # Показать новую страницу
        self.pages[page_key].pack(fill=tk.BOTH, expand=True)
        
        # Обновить текст кнопки Start/Stop
        if page_key == "main":
            self.start_button.config(text=self.texts["start"] if self.process is None 
                                   else self.texts["stop"])
        
        # Подсветка активной кнопки меню
        for btn, key in zip(self.menu_buttons, ["main", "settings", "stats", "about"]):
            if key == page_key:
                btn.config(bg=self.primary_color, fg="#000000")
            else:
                btn.config(bg=self.sidebar_color, fg=self.text_color)

    def switch_page(self, page_key):
        if page_key != self.current_page:
            self.show_page(page_key)

    def toggle_script(self):
        if self.process is None:
            try:
                self.process = subprocess.Popen(["python", "main.py"])
                self.start_button.config(text=self.texts["stop"], bg=self.error_color)
                self.update_counter(1)
            except Exception as e:
                error_msg = f"Не удалось запустить скрипт: {str(e)}"
                self.log_error(error_msg)
                self.blink_button()
        else:
            self.process.terminate()
            self.process = None
            self.start_button.config(text=self.texts["start"], bg=self.primary_color)

    def blink_button(self, count=0):
        if count < 6:  # 3 мигания (вкл/выкл)
            color = self.error_color if count % 2 == 0 else self.primary_color
            self.start_button.config(bg=color)
            self.root.after(200, lambda: self.blink_button(count + 1))

    def log_error(self, error_msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {error_msg}\n"
        
        try:
            with open("Log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Ошибка записи в лог-файл: {str(e)}")
        
        messagebox.showerror("Ошибка", error_msg)

    def get_last_error(self):
        try:
            with open("Log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    return lines[-1].strip()
        except FileNotFoundError:
            pass
        return self.texts["last_error"] + " -"

    def get_last_text(self):
        try:
            with open("last_dialog.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            pass
        return self.texts["last_text"] + " -"

    def get_counter(self):
        try:
            with open("setting.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    return lines[2].strip()
        except FileNotFoundError:
            pass
        return "0"

    def update_counter(self, increment=0):
        try:
            # Читаем текущие настройки
            with open("setting.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Обновляем счетчик
            if len(lines) >= 3:
                try:
                    count = int(lines[2].strip()) + increment
                    lines[2] = f"{count}\n"
                except ValueError:
                    lines[2] = "1\n"
            else:
                while len(lines) < 3:
                    lines.append("\n")
                lines[2] = "1\n"
            
            # Записываем обратно
            with open("setting.txt", "w", encoding="utf-8") as f:
                f.writelines(lines)
                
        except FileNotFoundError:
            # Если файла нет, создаем новый
            with open("setting.txt", "w", encoding="utf-8") as f:
                f.write("\n\n1\n\n")  # Пустые строки для разрешения и языка

    def toggle_custom_resolution(self):
        if self.custom_res_var.get():
            self.custom_frame.pack(pady=10)
            self.resolution_menu.config(state="disabled")
        else:
            self.custom_frame.pack_forget()
            self.resolution_menu.config(state="readonly")

    def apply_custom_resolution(self):
        width = self.width_entry.get()
        height = self.height_entry.get()
        
        if width.isdigit() and height.isdigit():
            self.save_resolution(width, height)
            messagebox.showinfo("Успех", f"Разрешение установлено {width}x{height}")
        else:
            messagebox.showerror("Ошибка", "Введите числовые значения!")

    def update_resolution(self, event):
        selected = self.resolution_var.get()
        for res in self.resolutions:
            if res[0] == selected:
                self.save_resolution(res[1], res[2])
                break

    def save_resolution(self, width, height):
        try:
            with open("setting.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Обновляем первые две строки (ширина и высота)
            if len(lines) >= 2:
                lines[0] = f"{width}\n"
                lines[1] = f"{height}\n"
            else:
                lines = [f"{width}\n", f"{height}\n"]
                if len(lines) < 4:
                    lines.extend(["\n"] * (4 - len(lines)))
            
            with open("setting.txt", "w", encoding="utf-8") as f:
                f.writelines(lines)
                
        except FileNotFoundError:
            with open("setting.txt", "w", encoding="utf-8") as f:
                f.write(f"{width}\n{height}\n\n")

    def save_all_settings(self):
        """Сохраняет все настройки в файл"""
        try:
            # Получаем текущие настройки
            with open("setting.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Обновляем разрешение
            selected_res = self.resolution_var.get()
            for res in self.resolutions:
                if res[0] == selected_res:
                    lines[0] = f"{res[1]}\n"
                    lines[1] = f"{res[2]}\n"
                    break
            
            # Обновляем задержку (строка 4)
            if len(lines) >= 4:
                lines[3] = f"{self.delay_var.get()}\n"
            else:
                while len(lines) < 4:
                    lines.append("\n")
                lines[3] = f"{self.delay_var.get()}\n"
            
            # Обновляем голос (строка 5)
            if len(lines) >= 5:
                lines[4] = f"{self.voice_var.get()}\n"
            else:
                while len(lines) < 5:
                    lines.append("\n")
                lines[4] = f"{self.voice_var.get()}\n"
            
            # Сохраняем
            with open("setting.txt", "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            messagebox.showinfo("Сохранено", "Настройки успешно сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Стили для combobox
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Custom.TCombobox', 
                   fieldbackground='#3a3a3a', 
                   foreground='#ffffff', 
                   background='#3a3a3a',
                   selectbackground='#4a4a4a',
                   selectforeground='#ffffff')
    
    style.configure('Custom.TCheckbutton', 
                   background='#2a2a2a', 
                   foreground='#ffffff',
                   indicatorcolor='#FFA726')
    
    style.configure('Custom.TButton', 
                   background='#FFA726', 
                   foreground='#000000',
                   bordercolor='#FFA726',
                   focusthickness=0,
                   focuscolor='none')
    
    app = TTSApp(root)
    root.mainloop()