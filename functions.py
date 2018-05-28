# -*- coding: utf-8
import requests
import psycopg2
import redis
import telebot
import config
import data
import lang as l
import text_handler as t


def check_id_in_db(user):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT id FROM public.users WHERE id = {user.id}'
    cur.execute(query)
    status = cur.fetchone()
    if not status:
        if not user.first_name:
            user.first_name = 'NULL'
        if not user.last_name:
            user.last_name = 'NULL'
        query = f'INSERT INTO public.users (id, first_name, last_name)' \
                f'VALUES (' \
                f'\'{user.id}\', \'{user.first_name}\', \'{user.last_name}\')'
        cur.execute(query)
        conn.commit()
    conn.close()


def check_location(user, lat, long, bot):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    lang = l.get_lang_grom_redis(user)
    query = f'SELECT latitude, longitude FROM locations ' \
            f'WHERE id = {user}'
    cur.execute(query)
    locations_in_db = cur.fetchone()
    if not locations_in_db:

        tz = get_tz_by_location([lat, long])
        if tz != '':
            query = f'INSERT INTO locations (id, latitude, longitude) ' \
                    f'VALUES (\'{user}\', \'{lat}\', \'{long}\')'
            cur.execute(query)
            conn.commit()
            check_tz(user, tz)
            if lang == 'Русский':
                response = 'Координаты получены, теперь вы можете ' \
                           'начать работать с ботом'
            elif lang == 'English':
                response = 'Location has been received, now you can start ' \
                           'working with the bot'
            bot.send_message(user, response)
            return True
        else:
            if lang == 'Русский':
                response = 'Не получилось определить часовой пояс. Возможно ' \
                           'вы находитесь далеко от берега или указали ' \
                           'неверные координаты. Попробуйте отправить свое' \
                           ' местоположение еще раз'
            elif lang == 'English':
                response = 'Time zone could not be determined. Рrobably, you' \
                           ' аre far from сoast or indicate incorrect ' \
                           'coordinates. Try to send your location again.'
            bot.send_message(user, response)

    # если координаты в бд отличаются от присланных, обновляем бд
    elif lat != locations_in_db[0] or long != locations_in_db[1]:
        loc = [lat, long]
        tz = get_tz_by_location(loc)
        lang = l.get_lang_grom_redis(user)
        if tz != '':
            check_tz(user, tz)
            query = f'UPDATE locations SET ' \
                    f'latitude = \'{lat}\', longitude = \'{long}\'' \
                    f'WHERE id = {user}'
            if lang == 'Русский':
                response = 'Координаты обновлены'
            elif lang == 'English':
                response = 'Location updated'
            bot.send_message(user, response)
            cur.execute(query)
            conn.commit()
            conn.close()
            return True
        else:
            if lang == 'Русский':
                response = 'Не получилось определить часовой пояс. Возможно ' \
                           'вы находитесь далеко от берега или указали ' \
                           'неверные координаты. Попробуйте отправить свое' \
                           ' местоположение еще раз'
            elif lang == 'English':
                response = 'Time zone could not be determined. Рrobably, you' \
                           ' аre far from сoast or indicate incorrect ' \
                           'coordinates. Try to send your location again.'
            bot.send_message(user, response)
            return False


def get_location_by_id(user_id):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT latitude, longitude FROM locations WHERE id = {user_id}'
    cur.execute(query)
    location = cur.fetchone()
    if not location:
        return False
    return location


def check_tz(user, tz):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT tz FROM public.tz WHERE id = {user}'
    cur.execute(query)
    time_zone = cur.fetchone()
    if not time_zone:
        query = f'INSERT INTO public.tz (id, tz) VALUES ({user}, \'{tz}\')'
        cur.execute(query)
        conn.commit()
    elif time_zone != tz:
        query = f'UPDATE public.tz SET tz = \'{tz}\' WHERE id = {user}'
        cur.execute(query)
        conn.commit()


def get_tz_by_id(user_id):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT public.tz.tz FROM public.tz WHERE id = {user_id}'
    cur.execute(query)
    tz = cur.fetchone()
    if not tz:
        return False
    return tz[0]


def get_tz_by_location(loc):
    url = f'http://api.geonames.org/timezoneJSON'
    params = {'username': 'arlas',
              'lat': loc[0],
              'lng': loc[1]
              }
    tz_data = requests.get(url, params=params).json()
    tz = tz_data.get('timezoneId', '')
    return tz


def get_main_menu(lang):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if lang == 'English':
        user_markup.row('Zmanim', 'Shabbos', 'Holidays')
        user_markup.row('Daf Yomi', 'Rosh Chodesh', 'Fast days')
        user_markup.row('Extended Zmanim', 'Update location')
        user_markup.row('Language', 'F.A.Q.', 'Contact')
    elif lang == 'Русский':
        user_markup.row('Зманим', 'Шаббат', 'Праздники')
        user_markup.row('Даф Йоми', 'Рош Ходеш', 'Посты')
        user_markup.row('Расширенные Зманим', 'Обновить местоположение')
        user_markup.row('Сменить язык', 'ЧаВо', 'Сообщить об ошибке')
    return user_markup


def get_holiday_menu(lang):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if lang == 'Русский':
        user_markup.row('Рош Ашана', 'Йом Кипур')
        user_markup.row('Суккот', 'Шмини Ацерет')
        user_markup.row('Ханука', 'Ту биШват', 'Пурим')
        user_markup.row('Пейсах', 'Лаг баОмер', 'Шавуот')
        user_markup.row('15 Ава', 'Израильские праздники')
        user_markup.row('Назад')
    elif lang == 'English':
        user_markup.row('Rosh HaShanah', 'Yom Kippur')
        user_markup.row('Succos', 'Shmini Atzeres')
        user_markup.row('Chanukah', 'Tu BShevat', 'Purim')
        user_markup.row('Pesach', 'Lag BaOmer', 'Shavuot')
        user_markup.row('Tu BAv', 'Israel holidays')
        user_markup.row('Back')
    return user_markup


def get_fast_menu(lang):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if lang == 'Русский':
        user_markup.row('Пост Гедалии', '10 Тевета')
        user_markup.row('Пост Эстер', '17 Таммуза')
        user_markup.row('9 Ава')
        user_markup.row('Назад')
    elif lang == 'English':
        user_markup.row('Tzom Gedaliah', 'Asarah BTevet')
        user_markup.row('Taanit Esther', 'Shiva Asar BTammuz')
        user_markup.row('Tisha BAv')
        user_markup.row('Back')
    return user_markup


if __name__ == '__main__':
    pass
