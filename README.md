# SleepBot — Telegram Sleep Tracker (Console School Project)

## 📌 Описание  
**SleepBot** — это простой Telegram-бот, разработанный для отслеживания и улучшения качества сна.  
Пользователи могут начинать и завершать сеансы сна, оставлять заметки, оценивать качество сна и просматривать историю записей.  
Это учебный проект, реализованный в рамках школьного задания.

## ⚙️ Функциональность  
- `/start` — приветствие и регистрация пользователя  
- `/help` — список всех доступных команд  
- `/id` — отображает ваш Telegram ID  
- `/sleep` — начало сеанса сна  
- `/wake` — завершение сеанса сна  
- `/quality [оценка от 1 до 10]` — оценка качества сна  
- `/notes [текст заметки]` — добавление комментария к последнему сеансу  
- `/journal` — отображение всех записей о сне

## 🛠️ Технологии  
- Python 3  
- [pyTelegramBotAPI (telebot)](https://github.com/eternnoir/pyTelegramBotAPI)  
- SQLite3

## 📁 Структура проекта  
<pre>
sleepbot/
├── main.py         # Точка входа, логика команд и запуск бота
├── commands.py     # Работа с базой данных: создание, обновление, чтение записей
├── utils.py        # Вспомогательные функции: форматирование времени, проверка статуса пользователя
└── sleepbot.db     # База данных SQLite (создается автоматически)
</pre>

## 🚀 Как запустить  
1. Убедитесь, что у вас установлен Python 3.  
2. Установите зависимости:  
   ```bash
   pip install pyTelegramBotAPI
3. Замените токен бота в `main.py`:
   ```bash
   sleep_bot = SleepBot('<ваш_токен_бота>')
   ```
4. Запустите бота:
   ```bash
   python main.py
   ```
5. Откройте Telegram и найдите своего бота — теперь можно взаимодействовать с ним через команды.
 
## 📝 Примечания
- Таблицы базы данных создаются автоматически при запуске.
- Пользователь добавляется в базу при первой команде /start.
- Команды /sleep и /wake должны использоваться поочерёдно.
