import sqlite3


def read_txt_doc(file_path):
    with open(file_path) as file:
        lines_from_file = file.read().splitlines()

    songs_from_file = [i.strip() for i in lines_from_file]

    return [x.lower() for x in songs_from_file if x]


def create_db():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Создаем таблицу Users
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


def record_db_line(song_name, duration):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Добавляем нового пользователя
    cursor.execute('INSERT INTO CS_tracklist (song_name, duration) VALUES (?, ?)', (song_name, duration))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def all_songs():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Выбираем всех пользователей
    cursor.execute('SELECT * FROM CS_tracklist')
    lines = cursor.fetchall()

    # Закрываем соединение
    connection.close()

    return lines


def remove_song(song_name):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Удаляем пользователя "newuser"
    cursor.execute('DELETE FROM CS_tracklist WHERE song_name = ?', (song_name,))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def check_if_track_is_common(track):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Выбираем длительности всех песен
    # print(f"SELECT EXISTS(SELECT 1 FROM CS_tracklist WHERE song_name='{track}')")
    result = cursor.execute(f"SELECT EXISTS(SELECT 1 FROM CS_tracklist WHERE song_name='{track}')").fetchone()[0]
    # print(result)

    # Закрываем соединение
    connection.close()

    return result


def calc_duration_of_all_from_tracklist(track_list):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Выбираем длительности выбранных песен
    query = f"SELECT SUM(duration) FROM CS_tracklist WHERE song_name IN ({track_list})"
    # print(query)
    cursor.execute(query)
    duration = cursor.fetchall()

    # Закрываем соединение
    connection.close()

    return duration[0][0]


def delete_db():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('CS_tracklist.db')
    cursor = connection.cursor()

    # Удаляем таблицу Users
    cursor.execute('''
    DROP TABLE CS_tracklist
    ''')

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


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

    return f"{hour}:{minutes}:{seconds}"


def add_not_found_songs(track_list):
    for track in track_list:
        if not check_if_track_is_common(track):
            song_name = track
            duration = get_sec(input(f"Какая длительность у {track}? (M:SS): "))
            record_db_line(song_name, duration)


file_path = "/Users/user/Desktop/songsCS.txt"

user_input = ""

create_db()

# Основная работа программы
while user_input != "выйти":
    user_input = input("Команда: ").lower()
    if "добавить песню" in user_input:
        song_name = input("Название песни: ")
        duration = get_sec(input("Продолжительность песни: "))

        record_db_line(song_name, duration)

    elif "все песни" in user_input:
        print("все")
        for i in all_songs():
            print(i)

    elif "удалить песню" in user_input:
        song_to_remove = input("Какую песню удалить?: ")
        remove_song(song_to_remove)

    elif "удалить все" in user_input:
        delete_db()

    elif "длительность треклиста" in user_input:
        # Читаем список песен из файла
        track_list = read_txt_doc(file_path)
        str_track_list_for_sql = ', '.join(f"'{i}'" for i in track_list)
        print(track_list)
        add_not_found_songs(track_list)
        print(time_str_from_secs(calc_duration_of_all_from_tracklist(str_track_list_for_sql)))

    elif "выйти" in user_input:
        print("я мухожук")
