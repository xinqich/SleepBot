import telebot

from utils import *
from commands import *


class SleepBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.setup_handlers()

    def start(self, message):
        conn = get_db_connection()
        add_user(conn, message.from_user.id, message.from_user.username)
        conn.close()

        self.bot.send_message(message.chat.id, '''
Привет! Я бот, который помогает тебе отслеживать качество сна. 
Чтобы увидеть список команд, введи /help''')

    def sleep(self, message):
        conn = get_db_connection()
        user_id = message.from_user.id

        if not check_if_awake(conn, user_id):
            self.bot.reply_to(message,
                              'Ты еще не закончил предыдущий сеанс сна. Сначала закончи его командой /wake')
            return

        create_record(conn, user_id)
        conn.close()

        self.bot.send_message(message.chat.id, 'Спокойной ночи! Дай мне знать когда ты проснешься командой /wake')

    def help(self, message):
        self.bot.send_message(message.chat.id, ''' Список доступных команд: 
/start - приветствие
/help - список команд
/id - ваш id пользователя
/sleep - сообщить о начале сна
/wake - сообщить о конце сна
/quality [число] - оценить свой сон от 1 до 10
/notes [комментарий]- оставить комментарий
/journal - записи о прошлых сеансах''')

    def id(self, message):
        self.bot.reply_to(message, f'Твой id: {message.from_user.id}')

    def wake(self, message):
        conn = get_db_connection()
        user_id = message.from_user.id

        if check_if_awake(conn, user_id):
            self.bot.reply_to(message, 'Ты еще не начинал сеанс сна. Используй команду /sleep для того, чтобы начать')
            return

        update_record(conn, user_id)
        conn.close()

        self.bot.reply_to(message, 'Доброе утро! Не забудь оставить отзыв о качестве сна.')

    def quality(self, message):
        conn = get_db_connection()
        user_id = message.from_user.id

        if not check_if_awake(conn, user_id):
            self.bot.reply_to(message, 'Ты не можешь ставить оценки во время сна. Сначала закончи сон командой /wake')
            return

        split_message = message.text.split()

        if len(split_message) != 2:
            self.bot.reply_to(message, 'Неправильное использование команды.')
            return

        try:
            sleep_quality = int(split_message[1])
            if not 1 <= sleep_quality <= 10:
                self.bot.reply_to(message, 'Неккоректный ввод. Оценка должна быть числом в диапазоне от 1 до 10.')
                return
        except ValueError:
            self.bot.reply_to(message, 'Неккоректный ввод. Оценка должна быть числом от 1 до 10.')
            return

        update_record(conn, user_id, sleep_quality)
        conn.close()

        self.bot.reply_to(message, 'Оценка записана!')

    def notes(self, message):
        conn = get_db_connection()
        user_id = message.from_user.id
        if not check_if_awake(conn, user_id):
            self.bot.reply_to(message, 'Ты не можешь писать заметки во время сна. Сначала закончи сон командой /wake')
            return

        split_message = message.text.split()

        if len(split_message) < 2:
            self.bot.reply_to(message, 'Неправильное использование команды.')

        update_record(conn, user_id=user_id, notes=' '.join(split_message[1:]))
        conn.close()

        self.bot.reply_to(message, 'Заметка записана!')

    def journal(self, message):
        conn = get_db_connection()
        user_id = message.from_user.id
        username = message.from_user.username

        if not check_if_awake(conn, user_id):
            self.bot.reply_to(message,
                              'Ты не можешь просматривать журнал во время сна. Сначала закончи сон командой /wake')
            return

        journal = show_records(conn, user_id)

        if not journal:
            self.bot.reply_to(message, 'У тебя еще нет записей о снах. Ты можешь начать новую командой /sleep')
            return

        self.bot.send_message(message.chat.id, f'Все записи пользователя {username} ({user_id}):\n{journal}')

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.start(message)

        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            self.help(message)

        @self.bot.message_handler(commands=['id'])
        def handle_id(message):
            self.id(message)

        @self.bot.message_handler(commands=['sleep'])
        def handle_sleep(message):
            self.sleep(message)

        @self.bot.message_handler(commands=['wake'])
        def handle_wake(message):
            self.wake(message)

        @self.bot.message_handler(commands=['quality'])
        def handle_quality(message):
            self.quality(message)

        @self.bot.message_handler(commands=['notes'])
        def handle_notes(message):
            self.notes(message)

        @self.bot.message_handler(commands=['journal'])
        def handle_journal(message):
            self.journal(message)

    def run(self):
        self.bot.polling(none_stop=True)


# Создание экземпляра бота и запуск
sleep_bot = SleepBot('6789822373:AAHLeiExeAz4mkA0seZNnqNQTBbCnVHN61k')
create_tables()
sleep_bot.run()
