import os

import telebot
import sqlite3


def get_sec(time_str):
    """Get seconds from time."""
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)


def time_str_from_secs(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    hour = f'0{hour}' if len(str(hour)) < 2 else str(hour)
    seconds %= 3600
    minutes = seconds // 60
    minutes = f'0{minutes}' if len(str(minutes)) < 2 else str(minutes)
    seconds %= 60
    seconds = f'0{seconds}' if len(str(seconds)) < 2 else str(seconds)

    return f"{hour}:{minutes}:{seconds}" if hour != '00' else f"{minutes}:{seconds}"


def create_tracks_table():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Создаем таблицу CS_tracklist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CS_tracklist (
        id INTEGER PRIMARY KEY,
        song_name TEXT NOT NULL,
        duration INT NOT NULL
        )
        ''')

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def create_states_table():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Создаем таблицу User_states
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_states (
        user_id Uint64 PRIMARY KEY,
        state Utf8
        )
        ''')

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def record_db_line(song_name, duration):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Добавляем новый трек
    query = f'INSERT INTO CS_tracklist (song_name, duration) VALUES ("{song_name}", {duration})'
    cursor.execute(query)

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def check_if_track_is_common(track):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Проверяем есть ли строка с треком
    result = cursor.execute(f"SELECT EXISTS(SELECT 1 FROM CS_tracklist WHERE song_name='{track}')").fetchone()[0]

    # Закрываем соединение
    connection.close()

    return result


def remove_track_from_table(track_name):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Удаляем track
    cursor.execute('DELETE FROM CS_tracklist WHERE song_name = ?', (track_name,))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def get_state(user_id: int) -> str:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Получаем значение по user_id из таблицы User_states
    query = f'SELECT state FROM User_states WHERE user_id = {user_id}'
    result = cursor.execute(query).fetchone()

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

    return result[0]


def set_state(user_id: int, state: str) -> None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Создаем новую строку в таблице User_states
    if not cursor.execute(f"SELECT EXISTS(SELECT 1 FROM User_states WHERE user_id='{user_id}')").fetchone()[0]:
        query = f'INSERT INTO User_states (user_id, state) VALUES ({user_id}, "{state}")'
    else:
        query = f'UPDATE User_states SET state = "{state}" WHERE user_id = {user_id}'
    cursor.execute(query)

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def clear_state(user_id: int) -> None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Создаем новую строку в таблице User_states
    query = f'UPDATE User_states SET state = NULL WHERE user_id = {user_id}'
    cursor.execute(query)

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def set_duration_of_track(duration):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # TODO Переделать костыль с -1
    query = f'UPDATE CS_tracklist SET duration = {duration} WHERE duration = -1'
    cursor.execute(query)

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def handle_track_name(message):
    track_name = message.text.lower()
    msg = bot.send_message(message.chat.id, f'Введите длительность трека "{track_name}" в формате: M:SS.'
                                            f'\n\nНапример 3:07 /cancel')
    bot.register_next_step_handler(msg, handle_track_name_and_duration, track_name)


def handle_duration(message):
    try:
        duration = get_sec(message.text)
        set_duration_of_track(duration)
        bot.send_message(message.chat.id, 'Трек успешно добавлен')
    except:
        bot.send_message(message.chat.id, 'Неверный формат длительности. Попробуйте еще раз: /add_track')

    clear_state(message.from_user.id)


def handle_track_name_and_duration(message, track_name):
    try:
        duration = get_sec(message.text)
        record_db_line(track_name, duration)
        bot.send_message(message.chat.id, 'Трек успешно добавлен')
    except:
        bot.send_message(message.chat.id, 'Неверный формат длительности. Попробуйте еще. /add_track')

    clear_state(message.from_user.id)


def handle_track_name_to_remove(message):
    track_name = message.text.lower()
    remove_track_from_table(track_name)
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, f'Трек "{track_name}" успешно удалён')


def format_data_like_columns(rows):  # TODO сделать выравнивание по времени по правому краю
    lens = []
    for col in zip(*rows):
        lens.append(max([len(v) for v in col]))
    format = "  ".join(["{:<" + str(l) + "}" for l in lens])
    res = ''
    for row in rows:
        res += (format.format(*row) + '\n')

    return res


def get_duration_of_track(track):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    query = f'SELECT duration FROM CS_tracklist WHERE song_name = "{track}"'
    result = cursor.execute(query).fetchone()

    connection.close()

    return result[0]


def calc_duration_of_all_from_tracklist(track_list):
    res = 0
    for track in track_list:
        if check_if_track_is_common(track):
            res += get_duration_of_track(track)
    return res


def get_not_found_tracks(track_list):
    res = []
    for track in track_list:
        if not check_if_track_is_common(track):
            res.append(track)
    return res


def handle_track_list(message):
    # Сформируем из сообщения список песен
    track_list = [t.strip().lower() for t in message.text.splitlines() if t]

    not_found_tracks = get_not_found_tracks(track_list)
    if len(not_found_tracks) == 0:  # TODO переделать на пользовательский ввод сообщением

        rows_data = get_rows_data(track_list)
        rows_data.append((0, '_____________', 0))
        rows_data.append((0, 'Итого выходит', calc_duration_of_all_from_tracklist(track_list)))

        answer_list = format_data_like_columns([(f'{r[1]}',
                                                 f'{time_str_from_secs(r[2]) if r[2] else ''}') for r in rows_data])

        answer = f"```Посчитал:\n{answer_list}\n```"
        bot.send_message(message.chat.id, answer, parse_mode='MarkdownV2')
        clear_state(message.from_user.id)

    else:
        answer_list = format_data_like_columns([(f'{r}', '??:??') for r in not_found_tracks])
        answer = f"```Неизвестные:\n{answer_list}\n```"
        bot.send_message(message.chat.id, answer, parse_mode='MarkdownV2')
        bot.send_message(message.chat.id, 'Используйте команду /add_track , чтобы добавить новую песню')

        clear_state(message.from_user.id)


def get_rows_data(track_list=None):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    #
    if track_list is None:
        query = f"SELECT * FROM CS_tracklist"
        cursor.execute(query)
        rows = cursor.fetchall()
    else:
        rows = []
        for t in track_list:
            query = f"SELECT * FROM CS_tracklist WHERE song_name = '{t}'"
            cursor.execute(query)
            rows.append(cursor.fetchone())

    # Закрываем соединение
    connection.close()

    return rows


bot = telebot.TeleBot(os.environ["TOKEN"])

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand('start', 'привет!'),
        telebot.types.BotCommand('help', 'помогу, чем смогу'),
        telebot.types.BotCommand('all', 'все песни'),
        telebot.types.BotCommand('calc', 'длительность сетлиста'),
        telebot.types.BotCommand('add_track', 'добавить песню'),
        telebot.types.BotCommand('remove_track', 'удалить песню'),
        telebot.types.BotCommand('cancel', 'отмена')
    ]
)

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

create_tracks_table()
create_states_table()


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.reply_to(message, 'Я бот, посчитаю длительность сетлиста для вашего выступления. '
                          'Известные мне команды: \n\n'
                          '/calc - длительность сетлиста\n'
                          '/all - все известные мне из этого чата песни\n'
                          '/add_track - добавить песню\n'
                          '/remove_track - удалить песню')


@bot.message_handler(commands=['all'])
def handle_all(message):
    found_rows = get_rows_data()
    answer = format_data_like_columns([(f'{r[1]}', time_str_from_secs(r[2])) for r in found_rows])
    bot.send_message(message.chat.id, f"```Все:\n{answer}\n```", parse_mode='MarkdownV2')


@bot.message_handler(commands=['calc'])
def handle_calc(message):
    # TODO сделать ввод с кнопок

    set_state(message.from_user.id, 'calc')
    bot.send_message(message.chat.id, 'Введите треклист в виде сообщения: \n\ntrack 1\ntrack 2\ntrack 3')


@bot.message_handler(commands=['add_track'])
def handle_add_track(message):
    set_state(message.from_user.id, 'track_name')
    bot.send_message(message.chat.id, 'Какое название трека? /cancel')


@bot.message_handler(commands=['remove_track'])
def handle_remove(message):
    set_state(message.from_user.id, 'remove')
    bot.send_message(message.chat.id, 'Какой трек удалить? /cancel')


@bot.message_handler(commands=['cancel'])
def handle_remove(message):
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, 'Всё, ладно... отмена')


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_state = get_state(message.from_user.id)

    if user_state == 'track_name':
        handle_track_name(message)
    elif user_state == 'duration':  # Не факт что теперь нужно, когда есть next_step_handler
        handle_duration(message)
    elif user_state == 'remove':
        handle_track_name_to_remove(message)
    elif user_state == 'calc':
        handle_track_list(message)
    else:
        bot.send_message(message.chat.id, 'Не понял команды. Справка: /help')


bot.polling(none_stop=True)
