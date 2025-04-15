def check_if_awake(conn, user_id):
    """
    Checks if the user is currently awake based on their latest sleep record.
    If their last wake time is valid, returns True, False otherwise

    :param conn: SQLite database connection object.
    :param user_id: ID of the user whose wake status is to be checked.
    :return: `True` if the user is awake or has no sleep records; `False` otherwise.
    """

    cursor = conn.cursor()
    all_records = cursor.execute('SELECT * FROM sleep_records WHERE user_id = (?)', (user_id,)).fetchall()
    last_wake_time = cursor.execute(
        '''
        SELECT wake_time 
        FROM sleep_records
        WHERE id = (SELECT max(id) FROM sleep_records WHERE user_id = ?)
        ''',
        (user_id,)
    ).fetchone()

    if isinstance(last_wake_time, tuple):
        last_wake_time = last_wake_time[0]

    if not all_records and not last_wake_time:
        return True

    return bool(last_wake_time)


def format_duration(seconds: int) -> str:
    """
    Converts a duration in seconds into a formatted string showing hours, minutes, and seconds.

    :param seconds: Duration in seconds.
    :return: Formatted duration string (e.g., Input: 5455 -> '1h 30m 45s').
    """

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    result = []
    if hours:
        result.append(f'{hours}h')
    if minutes:
        result.append(f'{minutes}m')
    if seconds:
        result.append(f'{seconds}s')

    return ' '.join(result)
