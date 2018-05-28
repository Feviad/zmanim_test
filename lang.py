import psycopg2
import redis
import config
import data


def set_lang(user, lang):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT lang FROM lang WHERE id = {user}'
    cur.execute(query)
    lang_in_db = cur.fetchone()
    if not lang_in_db:
        query = f'INSERT INTO lang VALUES ({user}, \'{lang}\')'
        cur.execute(query)
        conn.commit()
    elif lang_in_db[0] != lang:
        query = f'UPDATE lang SET lang = \'{lang}\' WHERE id = {user}'
        cur.execute(query)
        conn.commit()
    r = redis.StrictRedis()
    r.set(f'{user}', data.lang[lang])
    r.expire(f'{user}', 31536000)


def get_lang_by_id(user):
    conn = psycopg2.connect(dbname='jcalendarbot',
                            user='cloud-user',
                            host=config.HOST,
                            password='qwerty',
                            port=5432
                            )
    cur = conn.cursor()
    query = f'SELECT lang FROM lang WHERE id = {user}'
    cur.execute(query)
    lang_in_bd = cur.fetchone()
    if not lang_in_bd:
        return False
    else:
        r = redis.StrictRedis()
        r.set(f'{user}', data.lang[lang_in_bd[0]])
        r.expire(f'{user}', 31536000)
        return True


def get_lang_grom_redis(user):
    r = redis.StrictRedis()
    lang_in_redis = r.get(f'{user}')
    if not lang_in_redis:
        lang_in_db = l.get_lang_by_id(user)
        if not lang_in_db:
            return t.change_lang(user)
        else:
            r.set(f'{user}', data.lang[lang_in_db])
            r.expire(f'{user}', 31536000)
            lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]
    else:
        lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]
    return lang
