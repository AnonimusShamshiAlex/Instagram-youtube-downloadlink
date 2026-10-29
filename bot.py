import os
import re
import asyncio
import logging
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import yt_dlp

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Папка для временных файлов
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def is_valid_url(text: str) -> bool:
    """Простая проверка, является ли текст ссылкой."""
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, text) is not None


def download_video(url: str):
    """
    Скачивает видео по ссылке и возвращает путь к файлу.
    Поддерживает YouTube, Instagram и многие другие сайты через yt-dlp.
    """
    file_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_hash}.%(ext)s")

    ydl_opts = {
        # Лучшее качество до 720p, чтобы чаще влезать в лимит Telegram (50 МБ)
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        # Если Instagram/YouTube начнут требовать cookies — раскомментируйте строку ниже
        # и положите рядом файл cookies.txt (экспорт из браузера):
        # 'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # После слияния формат может стать .mp4
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                if os.path.exists(base + ".mp4"):
                    filename = base + ".mp4"
            return filename
    except Exception as e:
        logger.error(f"Ошибка скачивания {url}: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "👋 Привет! Я бот для скачивания видео.\n\n"
        "Просто отправь мне ссылку на видео с **YouTube** или **Instagram** (Reels, посты), "
        "и я постараюсь его скачать и отправить тебе.\n\n"
        "⚠️ **Важно:**\n"
        "• Telegram ограничивает размер файлов (обычно 50 МБ), поэтому я качаю видео в качестве до 720p.\n"
        "• Для Instagram может потребоваться авторизация, и некоторые ссылки могут не работать."
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает входящие сообщения, содержащие ссылки."""
    url = update.message.text.strip()

    if not is_valid_url(url):
        await update.message.reply_text("Пожалуйста, отправь корректную ссылку.")
        return

    status_msg = await update.message.reply_text("⏳ Скачиваю видео... Это может занять некоторое время.")

    # Скачивание в отдельном потоке, чтобы не блокировать бота
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, download_video, url)

    if not file_path or not os.path.exists(file_path):
        await status_msg.edit_text("❌ Не удалось скачать видео. Проверь ссылку или попробуй позже.")
        return

    # Проверка размера файла (лимит Telegram Bot API ~50 МБ)
    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:
        await status_msg.edit_text(
            f"⚠️ Видео слишком большое ({file_size // (1024 * 1024)} МБ). "
            "Telegram не позволяет отправлять файлы больше 50 МБ через бота."
        )
        os.remove(file_path)
        return

    try:
        await status_msg.edit_text("📤 Отправляю видео...")
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="Готово! 🎬",
                supports_streaming=True,
                read_timeout=300,   # ждём до 5 минут на загрузку
                write_timeout=300   # ждём до 5 минут на запись
            )
        # Удаляем сообщение-статус после успешной отправки
        try:
            await status_msg.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await status_msg.edit_text("❌ Ошибка при отправке видео в Telegram.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def main():
    """Запуск бота."""
    # ЗАМЕНИТЕ НА ВАШ ТОКЕН
    TOKEN = "9179792040:AAEdoAawKpNrl6bNwbtMayvW9HgXvzMDttg"

    # Увеличенные таймауты специально для отправки медиафайлов
    custom_request = HTTPXRequest(
        media_write_timeout=300.0,  # время на загрузку видео (5 минут)
        connect_timeout=30.0,       # время на подключение
        read_timeout=30.0           # время на ожидание ответа
    )

    application = Application.builder().token(TOKEN).request(custom_request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()