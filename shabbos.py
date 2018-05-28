import pytz
import requests
import data
from datetime import datetime, timedelta
import functions as f


URL = 'http://db.ou.org/zmanim/getCalendarData.php'


def get_next_weekday(startdate, weekday):
    d = datetime.strptime(startdate, '%Y-%m-%d')
    t = timedelta((7 + weekday - d.weekday()) % 7)
    return (d + t).strftime('%Y-%m-%d')


def get_shabbos_string(loc, lang):
    tz = f.get_tz_by_location(loc)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    date_str = f'{now.year}-{now.month}-{now.day}'
    shabbat_date = get_next_weekday(date_str, 5)
    month = shabbat_date[5:7:]
    day = shabbat_date[8::]
    year = shabbat_date[:4:]
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{month}/{day}/{year}',
              'lat': loc[0],
              'lng': loc[1]
              }
    shabbat = requests.get(URL, params=params)
    shabbat_dict = shabbat.json()
    shabbat_str = ''

    if shabbat_dict['parsha_shabbos'] == 'YOM_KIPPUR':
        if lang == 'Русский':
            shabbat_str = '*Шаббат*\n\n📜' \
                          '🕯 *Зажигание свечей:* {}\n' \
                          '*Внимание!* Этот шаббат совпадает с днём '\
                          'Йом Киппура!' \
                .format(shabbat_dict['candle_lighting_shabbos'][:-3:])
        elif lang == 'English':
            shabbat_str = '*Shabbos*\n\n📜' \
                          '🕯 *Candle lighting:* {}\n' \
                          '*Notice!* This shabbat is Yom Kippur!' \
                .format(shabbat_dict['candle_lighting_shabbos'][:-3:])
        return shabbat_str

    if shabbat_dict['parsha_shabbos'] == 'SUCCOS_III':

        if shabbat_dict['zmanim']['sunset'] == 'X:XX:XX':
            if lang == 'Русский':
                shabbat_str = '*Шаббат*\n\n' \
                              'В данных широтах невозможно определить' \
                              ' зманим из-за полярного дня/полярной ночи'
            elif lang == 'English':
                shabbat_str = '*Shabbos*\n\n' \
                              'In these latitudes zmanim is impossible' \
                              ' to determine because of polar night/day'
            return shabbat_str

        if shabbat_dict['zmanim']['tzeis_850_degrees'] == 'X:XX:XX':
            # высчитываем полночь, прибавляя 12 часов
            chazot_time = datetime.strptime(shabbat_dict['zmanim']['chatzos'],
                                            "%H:%M:%S")
            chazot_delta = timedelta(hours=12)
            chazot_laila = str(datetime.time(chazot_time + chazot_delta))
            shabbat_dict['zmanim']['tzeis_850_degrees'] = chazot_laila
        if shabbat_dict['zmanim']['alos_ma'] == 'X:XX:XX':
            if lang == 'Русский':
                shabbat_str = '*Шаббат*\n\n' \
                              '🕯 *Зажигание свечей:* {}\n' \
                              '✨ *Выход звёзд:* {}\n\n' \
                              '*Внимание!* Необходимо уточнить' \
                              ' время зажигания свечей у раввина общины.' \
                    .format(shabbat_dict['candle_lighting_shabbos'][:-3:],
                            shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
            elif lang == 'English':
                shabbat_str = '*Shabbos*\n\n' \
                              '🕯 *Candle lighting:* {}\n' \
                              '✨ *Tzeit hakochavim:* {}\n\n' \
                              '*Notice!* You should specify time of candle' \
                              ' lighting with the community rabbi.' \
                    .format(shabbat_dict['candle_lighting_shabbos'][:-3:],
                            shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
        else:
            if lang == 'Русский':
                shabbat_str = '*Шаббат*\n\n' \
                              '🕯 *Зажигание свечей:* {}\n' \
                              '✨ *Выход звёзд:* {}' \
                    .format(shabbat_dict['candle_lighting_shabbos'][:-3:],
                            shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
            elif lang == 'English':
                shabbat_str = '*Shabbos*\n\n' \
                              '🕯 *Candle lighting:* {}\n' \
                              '✨ *Tzeit hakochavim:* {}' \
                    .format(shabbat_dict['candle_lighting_shabbos'][:-3:],
                            shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])

        if tz in ['Asia/Jerusalem', 'Asia/Tel_Aviv', 'Asia/Hebron']:
            sunset = datetime.strptime(shabbat_dict['zmanim']['sunset'],
                                       "%H:%M:%S")
            delta_18 = timedelta(minutes=18)
            delta_30 = timedelta(minutes=30)
            delta_40 = timedelta(minutes=40)
            candle_18 = str(datetime.time(sunset - delta_18))
            candle_30 = str(datetime.time(sunset - delta_30))
            candle_40 = str(datetime.time(sunset - delta_40))
            if lang == 'Русский':
                shabbat_str = '*Шаббат*\n\n' \
                              '🕯 *Зажигание свечей:*\n' \
                              '*18* минут до шкии: {:.5s}\n' \
                              '*30* минут до шкии: {:.5s}\n' \
                              '*40* минут до шкии: {:.5s}\n\n' \
                              '✨ *Выход звёзд:* {}'.format(
                    candle_18, candle_30, candle_40,
                    shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
            elif lang == 'English':
                shabbat_str = '*Shabbos*\n\n' \
                              '🕯 *Зажигание свечей:*\n' \
                              '*18* minutes before sunset: {:.5s}\n' \
                              '*30* minutes before sunset: {:.5s}\n' \
                              '*40* minutes before sunset: {:.5s}\n\n' \
                              '✨ *Tzeit hakochavim:* {}'.format(
                    candle_18, candle_30, candle_40,
                    shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
        return shabbat_str


    if shabbat_dict['zmanim']['sunset'] == 'X:XX:XX':
        if lang == 'Русский':
            shabbat_str = '*Шаббат*\n\n📜 *Недельная глава:* {}\n\n' \
                          'В данных широтах невозможно определить' \
                          ' зманим из-за полярного дня/полярной ночи'\
                .format(data.parashat[shabbat_dict['parsha_shabbos']])
        elif lang == 'English':
            shabbat_str = '*Shabbos*\n\n📜 *Parshat hashavua:* {}\n\n' \
                          'In these latitudes zmanim is impossible' \
                          ' to determine because of polar night/day'\
                .format(shabbat_dict['parsha_shabbos'])
        return shabbat_str

    if shabbat_dict['zmanim']['tzeis_850_degrees'] == 'X:XX:XX':
        # высчитываем полночь, прибавляя 12 часов
        chazot_time = datetime.strptime(shabbat_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        chazot_laila = str(datetime.time(chazot_time + chazot_delta))
        shabbat_dict['zmanim']['tzeis_850_degrees'] = chazot_laila
    if shabbat_dict['zmanim']['alos_ma'] == 'X:XX:XX':
        if lang == 'Русский':
            shabbat_str = '*Шаббат*\n\n📜 *Недельная глава:* {}\n' \
                          '🕯 *Зажигание свечей:* {}\n' \
                          '✨ *Выход звёзд:* {}\n\n' \
                          '*Внимание!* Необходимо уточнить' \
                          ' время зажигания свечей у раввина общины.'\
                .format(data.parashat[shabbat_dict['parsha_shabbos']],
                        shabbat_dict['candle_lighting_shabbos'][:-3:],
                        shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
        elif lang == 'English':
            shabbat_str = '*Shabbos*\n\n📜 *Parshat hashavua:* {}\n' \
                          '🕯 *Candle lighting:* {}\n' \
                          '✨ *Tzeit hakochavim:* {}\n\n' \
                          '*Notice!* You should specify time of candle' \
                          ' lighting with the community rabbi.'\
                .format(shabbat_dict['parsha_shabbos'],
                        shabbat_dict['candle_lighting_shabbos'][:-3:],
                        shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
    else:
        if lang == 'Русский':
            shabbat_str = '*Шаббат*\n\n📜 *Недельная глава:* {}\n' \
                          '🕯 *Зажигание свечей:* {}\n' \
                          '✨ *Выход звёзд:* {}'\
                .format(data.parashat[shabbat_dict['parsha_shabbos']],
                        shabbat_dict['candle_lighting_shabbos'][:-3:],
                        shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
        elif lang == 'English':
            shabbat_str = '*Shabbos*\n\n📜 *Parshat hashavua:* {}\n' \
                          '🕯 *Candle lighting:* {}\n' \
                          '✨ *Tzeit hakochavim:* {}'\
                .format(shabbat_dict['parsha_shabbos'],
                        shabbat_dict['candle_lighting_shabbos'][:-3:],
                        shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
    if tz in ['Asia/Jerusalem', 'Asia/Tel_Aviv', 'Asia/Hebron']:
        sunset = datetime.strptime(shabbat_dict['zmanim']['sunset'],
                                   "%H:%M:%S")
        delta_18 = timedelta(minutes=18)
        delta_30 = timedelta(minutes=30)
        delta_40 = timedelta(minutes=40)
        candle_18 = str(datetime.time(sunset - delta_18))
        candle_30 = str(datetime.time(sunset - delta_30))
        candle_40 = str(datetime.time(sunset - delta_40))
        if lang == 'Русский':
            shabbat_str = '*Шаббат*\n\n📜 *Недельная глава:* {}\n' \
                          '🕯 *Зажигание свечей:*\n' \
                          '*18* минут до шкии: {:.5s}\n' \
                          '*30* минут до шкии: {:.5s}\n' \
                          '*40* минут до шкии: {:.5s}\n\n' \
                          '✨ *Выход звёзд:* {}'.format(
                           data.parashat[shabbat_dict['parsha_shabbos']],
                           candle_18, candle_30, candle_40,
                           shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
        elif lang == 'English':
            shabbat_str = '*Shabbos*\n\n📜 *Parshat hashavua:* {}\n' \
                          '🕯 *Зажигание свечей:*\n' \
                          '*18* minutes before sunset: {:.5s}\n' \
                          '*30* minutes before sunset: {:.5s}\n' \
                          '*40* minutes before sunset: {:.5s}\n\n' \
                          '✨ *Tzeit hakochavim:* {}'.format(
                           shabbat_dict['parsha_shabbos'],
                           candle_18, candle_30, candle_40,
                           shabbat_dict['zmanim']['tzeis_850_degrees'][:-3])
    return shabbat_str


if __name__ == '__main__':
    pass
