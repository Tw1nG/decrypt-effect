import asyncio
import random
import json
import os
import requests
from telethon import TelegramClient, events, Button

# Название конфигурационного файла
CONFIG_FILE = "dec.json"

# URL для проверки обновлений (укажите ссылку на raw-файл вашего скрипта на GitHub)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/ваш-username/ваш-репозиторий/main/ваш-скрипт.py"

# Текущая версия скрипта
SCRIPT_VERSION = "1.0.0"

# Загрузка конфигурации
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Ошибка чтения конфигурационного файла. Убедитесь, что файл не поврежден.")
            return None
    return None

# Сохранение конфигурации
def save_config(api_id, api_hash, phone_number, password=None):
    config = {
        "API_ID": api_id,
        "API_HASH": api_hash,
        "PHONE_NUMBER": phone_number,
        "PASSWORD": password,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# Загрузка конфигурации
config = load_config()

if config:
    API_ID = config.get("API_ID")
    API_HASH = config.get("API_HASH")
    PHONE_NUMBER = config.get("PHONE_NUMBER")
    PASSWORD = config.get("PASSWORD")
else:
    API_ID = input("Введите ваш API ID: ")
    API_HASH = input("Введите ваш API Hash: ")
    PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ")
    PASSWORD = input("Введите ваш пароль (если включена 2FA, иначе оставьте пустым): ") or None
    save_config(API_ID, API_HASH, PHONE_NUMBER, PASSWORD)

# Инициализация клиента
client = TelegramClient('decryption_effect', int(API_ID), API_HASH, system_version='4.16.30-vxCUSTOM')

# Настройки по умолчанию
typing_speed = 0.1
decrypt_delay = 2
cursor_symbol = "▮"
decrypt_style = "random"  # Стиль расшифровки по умолчанию

# Стили расшифровки
DECRYPT_STYLES = {
    "random": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()",
    "machine": "01!@#$%^&*()",
    "hieroglyphs": "𓃭𓃰𓃱𓃲𓃵𓃶𓃹𓃻𓃼𓄀𓄁𓄂𓄃𓄅𓄆𓄇𓄈𓄉𓄊𓄋𓄌𓄍𓄎𓄏",
    "emojis": "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠"
}

# Функция для проверки обновлений
async def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            # Ищем версию в удаленном скрипте
            if "SCRIPT_VERSION" in remote_script:
                remote_version = remote_script.split('SCRIPT_VERSION = "')[1].split('"')[0]
                if remote_version != SCRIPT_VERSION:
                    return f"Доступна новая версия: {remote_version} (текущая: {SCRIPT_VERSION}).\nОбновите скрипт!"
        return None
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")
        return None

# Функция для эффекта расшифровки
async def decrypt_effect(event, text):
    await event.delete()
    message = await event.respond("🔐 Расшифровка...")
    await asyncio.sleep(decrypt_delay)

    # Получаем символы для выбранного стиля
    symbols = DECRYPT_STYLES.get(decrypt_style, DECRYPT_STYLES["random"])
    encrypted_text = ''.join([random.choice(symbols) for _ in range(len(text))])
    
    for i in range(len(text)):
        decrypted_part = text[:i+1]
        remaining_encrypted = encrypted_text[i+1:]
        new_text = decrypted_part + remaining_encrypted + cursor_symbol

        try:
            await message.edit(new_text)
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            continue

        await asyncio.sleep(typing_speed)

    try:
        await message.edit(text)
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")

# Команда для настройки скорости
@client.on(events.NewMessage(pattern=r'/speed (\d*\.?\d+)'))
async def set_speed(event):
    global typing_speed
    try:
        new_speed = float(event.pattern_match.group(1))
        if 0.05 <= new_speed <= 1.0:
            typing_speed = new_speed
            await event.respond(f"⚙️ Скорость расшифровки изменена на {typing_speed} секунд.")
        else:
            await event.respond("⚠️ Укажите значение от 0.05 до 1.0 секунд.")
    except ValueError:
        await event.respond("⚠️ Некорректное значение. Укажите число.")

# Команда для настройки задержки
@client.on(events.NewMessage(pattern=r'/delay (\d+)'))
async def set_delay(event):
    global decrypt_delay
    try:
        new_delay = int(event.pattern_match.group(1))
        if 1 <= new_delay <= 10:
            decrypt_delay = new_delay
            await event.respond(f"⚙️ Задержка перед расшифровкой изменена на {decrypt_delay} секунд.")
        else:
            await event.respond("⚠️ Укажите значение от 1 до 10 секунд.")
    except ValueError:
        await event.respond("⚠️ Некорректное значение. Укажите число.")

# Команда для выбора стиля расшифровки
@client.on(events.NewMessage(pattern=r'/style (.+)'))
async def set_style(event):
    global decrypt_style
    style = event.pattern_match.group(1).lower()
    if style in DECRYPT_STYLES:
        decrypt_style = style
        await event.respond(f"🎨 Стиль расшифровки изменен на: {style}")
    else:
        await event.respond("⚠️ Некорректный стиль. Доступные стили: random, machine, hieroglyphs, emojis.")

# Основная команда
@client.on(events.NewMessage(pattern=r'/decrypt (.+)'))
async def decrypt_handler(event):
    try:
        text = event.pattern_match.group(1)
        await decrypt_effect(event, text)
    except Exception as e:
        print(f"Ошибка при выполнении эффекта расшифровки: {e}")
        await event.respond("⚠️ Произошла ошибка во время выполнения команды.")

# Уведомление о новых версиях при запуске
async def notify_updates():
    update_message = await check_for_updates()
    if update_message:
        await client.send_message(PHONE_NUMBER, update_message)

# Вывод доступных команд в консоль
def print_commands():
    print("\nДоступные команды:")
    print("- /decrypt <текст>: Запустить эффект расшифровки.")
    print("- /speed <число>: Установить скорость расшифровки (от 0.05 до 1.0 секунд).")
    print("- /delay <число>: Установить задержку перед расшифровкой (от 1 до 10 секунд).")
    print("- /style <стиль>: Выбрать стиль расшифровки (random, machine, hieroglyphs, emojis).")
    print("- /help: Показать список команд.\n")

# Основная функция
async def main():
    print("Запуск main()")
    await client.start(phone=PHONE_NUMBER, password=PASSWORD)
    print("Скрипт успешно запущен!")
    print_commands()  # Выводим список команд в консоль
    await notify_updates()  # Проверяем обновления при запуске
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())