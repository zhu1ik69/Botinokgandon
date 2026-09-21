import os
import hashlib
import requests

# Ссылка на файл с расписанием (прямая ссылка на скачивание из Nextcloud)
SHARE_URL = "https://cloud.nntc.nnov.ru/index.php/s/bATtPnHfoyFyzB5/download"
PAGE_URL = "https://cloud.nntc.nnov.ru/index.php/s/bATtPnHfoyFyzB5"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
HASH_FILE = "last_hash.txt"

GROUP_NAME = "3РПУ-24-1"


def get_file_bytes() -> bytes:
    r = requests.get(SHARE_URL, timeout=30, allow_redirects=True)
    r.raise_for_status()
    return r.content


def get_file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=30)
    resp.raise_for_status()


def main() -> None:
    data = get_file_bytes()
    new_hash = get_file_hash(data)

    old_hash = None
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            old_hash = f.read().strip()

    if old_hash is None:
        # Первый запуск — просто запоминаем текущий хэш, ничего не отправляем
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write(new_hash)
        print("Первый запуск: хэш сохранён, уведомление не отправлено.")
        return

    if new_hash != old_hash:
        send_telegram_message(
            f"⚠️ Расписание группы {GROUP_NAME} изменилось!\n{PAGE_URL}"
        )
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write(new_hash)
        print("Изменение найдено, уведомление отправлено.")
    else:
        print("Изменений нет.")


if __name__ == "__main__":
    main()
