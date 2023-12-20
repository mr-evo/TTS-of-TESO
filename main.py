import pyautogui
import keyboard

import speech_recognition
import pyttsx3

import time

import pytesseract
from PIL import Image

def wr_fl(): # запись конфига
    with open('setting.txt','w') as f:
        f.write(str(str(wind) + "\n" + str(hei)+ "\n" + str(nu)))

with open('setting.txt','r') as f: #Чтение конфига
        sett = str(f.read()).split('\n')
        wind = int(sett[0]) # ширина экрана
        hei = int(sett[1]) # высота экрана
        nu = int(sett[2]) # количество использований




tts = pyttsx3.init()
voices = tts.getProperty('voices')

# Задать голос по умолчанию
tts.setProperty('voice', 'ru')

# Установка голоса
for voice in voices:
    if voice.name == 'Microsoft Irina Desktop - Russian':
        tts.setProperty('voice', voice.id)


sr = speech_recognition.Recognizer()
sr.pause_threshold = 0.5
print('[info] -- Скрипт запущен')

if str(input("[info] -- Использовать разрешение " + str(wind) +"x"+ str(hei) + " (y/n): ")) == str("n"):
    wind = int(input("Введите ширину разрешения используемое в игре:  "))
    hei = int(input("Введите высоту разрешения используемое в игре:  "))
print("[info] -- Разрешение "+ str(wind) + "x" + str(hei) + " принято, программа успешно запущено \nУспешных срабатываний: "+str(nu))

# Будем делать только половину скрина
wind2 = int(wind)/2
pr = 0 # обяснения ниже

while True:  # создаем цикл
    if keyboard.is_pressed('e') or keyboard.is_pressed('t'):  # активация по нажатию
        time.sleep(1.5) # замделнеие, что открылся диолог 
        sc_shot = pyautogui.screenshot('foto.png', region=(int(wind2),0,int(wind2),int(hei)))  # делаем скрин
        print("[info_prog] -- Скрин сделан")

        img = Image.open("foto.png") # читаем скрин
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # указываем куда установлен тесеракт(по умолчанию)

        text = pytesseract.image_to_string(img, lang="rus") #выбор языка и использование нейронки для выявление текста
        try:
            if str(text.strip().split(' ')[0][0]) == "-": # перед именем пишется -, если есть, значит диолог
                print("[info_text] -- " + text.strip())
                tts.say(text.strip()) # озвучивание текста 
                tts.runAndWait()
                nu = int(nu) + 1 # счетчик использования
                wr_fl()
            else:
                print("[info_prog] -- Нажата кнопка <Е> , но текст диолога не найден")
                print("[info_text] -- " + text.strip())
        except:
            print("[info_error]")