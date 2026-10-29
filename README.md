# 🎬 Telegram Video Downloader Bot

Простой Telegram-бот, который скачивает видео по ссылке и отправляет его обратно в чат. Поддерживает **YouTube**, **Instagram** (Reels, посты) и тысячи других сайтов благодаря библиотеке [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

---

## ✨ Возможности

- 📥 Скачивание видео по ссылке (YouTube, Instagram, TikTok, Twitter и др.)
- 🎞️ Отправка видео прямо в Telegram
- ⚡ Асинхронная работа — бот не зависает во время скачивания
- 🧹 Автоматическое удаление временных файлов
- ⏱️ Увеличенный таймаут загрузки (до 5 минут) — больше никаких `Timed out`

---

## 📋 Требования

- **Python 3.9+**
- **FFmpeg** (обязательно — нужен для склейки видео и аудио)
- **Токен Telegram-бота** (получается у [@BotFather](https://t.me/BotFather))
- Стабильное интернет-соединение

---

## 🚀 Установка

### 1. Клонируйте репозиторий (или создайте папку вручную)

```bash
git clone https://github.com/AnonimusShamshiAlex/Instagram-youtube-downloadlink
cd Instagram-youtube-downloadlink
```

### 2. Установите Python-зависимости

```bash
pip install python-telegram-bot yt-dlp
```

### 3. Установите FFmpeg

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**macOS (через Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Скачайте сборку с [ffmpeg.org](https://ffmpeg.org/download.html), распакуйте и добавьте папку `bin` в `PATH`.

Проверка установки:
```bash
ffmpeg -version
```

### 4. Получите токен бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram.
2. Отправьте `/newbot`.
3. Придумайте имя и username.
4. Скопируйте токен вида `123456789:AAE...`.

### 5. Вставьте токен в код

Откройте `bot.py` и замените:

```python
TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"
```

на ваш реальный токен.

---

## ▶️ Запуск

```bash
python bot.py
```

В консоли появится:
```
Бот запущен...
```

Теперь найдите своего бота в Telegram, нажмите **Start** и отправьте любую ссылку на видео.

---

## 🖥️ Пример использования

```
Пользователь: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Бот: Скачиваю...
Бот: [отправляет видео]
```

---

## ⚠️ Ограничения

### 📦 Лимит размера файла

Обычный Telegram Bot API позволяет отправлять файлы **не больше 50 МБ**. Поэтому бот скачивает видео в качестве **до 720p**, чтобы чаще попадать в лимит.

Если видео больше 50 МБ — Telegram вернёт ошибку, и бот сообщит об этом. Обойти лимит можно только через [локальный сервер Bot API](https://github.com/tdlib/telegram-bot-api) (до 2 ГБ), но это требует отдельной настройки.

### 🔒 Instagram и YouTube

Иногда `yt-dlp` не может скачать видео без **cookies** (особенно из Instagram и для YouTube с серверных IP). Если бот выдаёт ошибку:

1. Установите расширение браузера **«Get cookies.txt LOCALLY»** (Chrome/Firefox).
2. Зайдите на сайт (Instagram/YouTube), где вы залогинены.
3. Экспортируйте cookies в файл `cookies.txt`.
4. Положите `cookies.txt` рядом с `bot.py`.
5. В `bot.py` раскомментируйте строку в `ydl_opts`:

```python
'cookiefile': 'cookies.txt',
```

---

## 🛠️ Возможные проблемы

| Проблема | Решение |
|---|---|
| `Timed out` при отправке видео | Уже исправлено через `media_write_timeout=300.0`. Если повторится — увеличьте значение. |
| `ffmpeg not found` | FFmpeg не установлен или не в `PATH`. Установите и перезапустите терминал. |
| `ERROR: Unsupported URL` | Ссылка не поддерживается `yt-dlp` или видео приватное. |
| `Sign in to confirm you're not a bot` (YouTube) | Нужны cookies — см. раздел выше. |
| `Login required` (Instagram) | Нужны cookies — см. раздел выше. |
| Бот молчит | Проверьте, что токен верный и процесс `python bot.py` запущен. |

---

## 📁 Структура проекта

```
.
├── bot.py          # основной код бота
├── README.md       # этот файл
├── cookies.txt     # (опционально) cookies для Instagram/YouTube
└── video.mp4       # временный файл, создаётся и удаляется автоматически
```

---

## 🧩 Как это работает

1. Пользователь отправляет ссылку в чат.
2. Бот вызывает `yt-dlp` в отдельном потоке (`run_in_executor`), чтобы не блокировать event loop.
3. `yt-dlp` скачивает видео в файл `video.mp4`.
4. Бот отправляет файл через `reply_video`.
5. Временный файл удаляется.

---

## 📜 Лицензия

Проект распространяется свободно — используйте, изменяйте и улучшайте на своё усмотрение.

---

## 🙏 Благодарности

- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) — обёртка над Telegram Bot API
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — мощный загрузчик видео
- [`FFmpeg`](https://ffmpeg.org/) — обработка медиафайлов
