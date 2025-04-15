import sqlite3
from sqlite3 import Connection
from datetime import datetime

from utils import format_duration


def get_db_connection():
    return sqlite3.connect('sleepbot.db')


def create_tables():
    conn: Connection = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY UNIQUE,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS sleep_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_time DATETIME,
            wake_time DATETIME DEFAULT NULL,
            duration REAL DEFAULT NULL,
            sleep_quality INTEGER DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sleep_record_id INTEGER,
            text TEXT DEFAULT NULL
        )
        '''
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_user(conn: Connection, user_id: int, name: str) -> None:
    """
    Function to add a user to the database
    :param conn: Connection object
    :param user_id: 10 digit user telegram id
    :param name: users nickname
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            INSERT INTO users (id, name) VALUES (?, ?)
            ''',
            (user_id, name)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return
    finally:
        cursor.close()


def create_record(conn: Connection, user_id: int) -> None:
    """
    Creates a new sleep record and associated notes entry for the user.

    :param conn: SQLite database connection object.
    :param user_id: ID of the user.
    :return: None
    """

    cursor = conn.cursor()

    cursor.execute('BEGIN TRANSACTION;')
    cursor.execute(
        '''
        INSERT INTO sleep_records (user_id, start_time) VALUES (?, ?)
        ''',
        (user_id, datetime.now().replace(microsecond=0))
    )
    cursor.execute(
        '''
        INSERT INTO notes (sleep_record_id) VALUES (?)
        ''',
        (cursor.lastrowid,)
    )
    cursor.execute('COMMIT;')
    conn.commit()
    cursor.close()


def update_record(conn, user_id, sleep_quality=None, notes=None) -> None:
    """
    Updates the latest sleep record for a given user.

    Depending on the provided arguments, the function will:
        - Update the sleep quality if `sleep_quality` is provided.
        - Update the notes if `notes` is provided.
        - Update the wake time and sleep duration if neither `sleep_quality` nor `notes` is provided.

    Note: don't use both sleep_quality and notes parameter in one call, only the first will be updated

    :param conn: SQLite database connection object.
    :param user_id: ID of the user whose record is being updated.
    :param sleep_quality: (Optional) New sleep quality rating.
    :param notes: (Optional) New notes for the sleep record.
    :return: None
    """

    cursor = conn.cursor()
    record_id = cursor.execute('SELECT max(id) FROM sleep_records WHERE user_id = (?)', (user_id,)).fetchone()[0]

    if sleep_quality:
        cursor.execute('UPDATE sleep_records SET sleep_quality = ? WHERE id = ?', (sleep_quality, record_id))
        conn.commit()
        cursor.close()
        return

    if notes:
        cursor.execute('UPDATE notes SET text = ? WHERE sleep_record_id = ?', (notes, record_id))
        conn.commit()
        cursor.close()
        return

    start_time = cursor.execute(
        '''
        SELECT start_time
        FROM sleep_records
        WHERE id = ?
        ''',
        (record_id,)).fetchone()[0]

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    wake_time = datetime.now().replace(microsecond=0)
    duration = wake_time - start_time

    cursor.execute(
        '''
        UPDATE sleep_records
        SET (wake_time, duration) = (?, ?)
        WHERE id = (?)
        ''',
        (wake_time, duration.total_seconds(), record_id)
    )
    conn.commit()
    cursor.close()


def show_records(conn, user_id):
    """
    Retrieves and formats all sleep records for a given user into a readable string.

    :param conn: SQLite database connection object.
    :param user_id: ID of the user whose records are to be retrieved.
    :return: Formatted string of all sleep records and notes, or `False` if no records exist.
    """
    cursor = conn.cursor()
    all_records = cursor.execute('SELECT * FROM sleep_records WHERE user_id = ?', (user_id,)).fetchall()
    all_notes = cursor.execute('SELECT * FROM notes').fetchall()
    cursor.close()

    if not all_records:
        return False

    names = ['Дата и время начала', 'Дата и время конца', 'Длительность', "Оценка", "Заметки"]
    final_string = ''

    for i in range(len(all_records)):
        final_string += f'{i + 1}. '
        for j in range(2, len(all_records[i]) + 1):
            if j == 4:
                final_string += f'{names[j - 2]}: {format_duration(int(all_records[i][j]))}\n'
                continue

            if j == 6:
                note_id = all_records[i][0] - 1
                final_string += f'{names[j - 2]}: {all_notes[note_id][2] if all_notes[note_id][2] else "Нет данных"}\n'
                continue

            final_string += f'{names[j - 2]}: {all_records[i][j] if all_records[i][j] else "Нет данных"}\n'

        final_string += '\n'

    return final_string

