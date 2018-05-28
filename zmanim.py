# -*- coding: utf-8
import requests
import re
import pytz
import data
from datetime import datetime, timedelta
import functions as f


URL = 'http://db.ou.org/zmanim/getCalendarData.php'


def get_zmanim(id, lang):
    tz = f.get_tz_by_id(id)
    loc = f.get_location_by_id(id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{now.month}/{now.day}/{now.year}',
              'lat': loc[0],
              'lng': loc[1]
              }
    zmanim = requests.get(URL, params=params)
    zmanim_dict = zmanim.json()
    month = re.search(r'[a-zA-z]+', zmanim_dict['hebDateString']) \
        .group(0)
    year_day = re.findall(r'\d+', zmanim_dict['hebDateString'])
    zmanim_str = ''
    if zmanim_dict['zmanim']['sunset'] == 'X:XX:XX':
        if lang == 'Русский':
            zmanim_str = 'В данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            zmanim_str = 'In these latitudes it is impossible to determine' \
                         ' because of polar night/day'
        return zmanim_str
    elif zmanim_dict['zmanim']['tzeis_595_degrees'] == 'X:XX:XX':
        chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        # высчитываем полночь, прибавляя 12 часов
        d6 = chazot_time + chazot_delta
        chazot_laila = str(datetime.time(d6))

        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))

        zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
        zmanim_dict['zmanim']['talis_ma'] = alot_chazot_time
        zmanim_dict['zmanim']['tzeis_595_degrees'] = chazot_laila
    elif zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX'\
            and zmanim_dict['zmanim']['talis_ma'] == 'X:XX:XX':
        chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))
        zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
        zmanim_dict['zmanim']['talis_ma'] = alot_chazot_time
    elif zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX':
        chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))
        zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time

    if lang == 'Русский':
        zmanim_str = '*Зманим*\n\n*Еврейская дата:* {} {} {} года\n' \
                     '*Рассвет* _(Алот Ашахар)_ *—* {:.5s}\n' \
                     '*Самое раннее время надевания ' \
                     'талита и тфилин* _(Мишеякир)_ *—* {:.5s}\n' \
                     '*Восход солнца* _(Нец Ахама)_ *—* {:.5s}\n' \
                     '*Конец времени чтения Шма* *—* {:.5s}\n' \
                     '*Конец времени чтения молитвы Амида* *—* {:.5s}\n' \
                     '*Полдень* _(Хацот)_ *—* {:.5s}\n' \
                     '*Самое раннее время Минхи*' \
                     ' _(Минха Гдола)_ *—* {:.5s}\n' \
                     '*Заход солнца* _(Шкия)_ *—* {:.5s}\n' \
                     '*Выход звезд* _(Цет Акохавим)_ *—* {:.5s}\n' \
            .format(year_day[0],
                    data.jewish_months_a[month],
                    year_day[1],
                    zmanim_dict['zmanim']['alos_ma'],
                    zmanim_dict['zmanim']['talis_ma'],
                    zmanim_dict['zmanim']['sunrise'],
                    zmanim_dict['zmanim']['sof_zman_shema_gra'],
                    zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                    zmanim_dict['zmanim']['chatzos'],
                    zmanim_dict['zmanim']['mincha_gedola_ma'],
                    zmanim_dict['zmanim']['sunset'],
                    zmanim_dict['zmanim']['tzeis_595_degrees']
                    )
    elif lang == 'English':
        zmanim_str = '*Zmanim*\n\n*Hebrew date*: {} {} {}\n' \
                     '*Alot Hashachar* *—* {:.5s}\n' \
                     '*Misheyakir* *—* {:.5s}\n' \
                     '*Hanetz Hachama* *—* {:.5s}\n' \
                     '*Sof Zman Shema* *—* {:.5s}\n' \
                     '*Sof Zman Tefilah* *—* {:.5s}\n' \
                     '*Chatzot Hayom* *—* {:.5s}\n' \
                     '*Mincha Gedolah* *—* {:.5s}\n' \
                     '*Shkiat Hachama* *—* {:.5s}\n' \
                     '*Tzeit Hakochavim* *—* {:.5s}\n' \
            .format(year_day[0],
                    month,
                    year_day[1],
                    zmanim_dict['zmanim']['alos_ma'],
                    zmanim_dict['zmanim']['talis_ma'],
                    zmanim_dict['zmanim']['sunrise'],
                    zmanim_dict['zmanim']['sof_zman_shema_gra'],
                    zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                    zmanim_dict['zmanim']['chatzos'],
                    zmanim_dict['zmanim']['mincha_gedola_ma'],
                    zmanim_dict['zmanim']['sunset'],
                    zmanim_dict['zmanim']['tzeis_595_degrees']
                    )
    return zmanim_str


def get_ext_zmanim(loc, lang):
    tz = f.get_tz_by_location(loc)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{now.month}/{now.day}/{now.year}',
              'lat': loc[0],
              'lng': loc[1]
              }
    zmanim = requests.get(URL, params=params)
    zmanim_dict = zmanim.json()
    month = re.search(r'[a-zA-z]+', zmanim_dict['hebDateString']).group(0)
    year_day = re.findall(r'\d+', zmanim_dict['hebDateString'])
    zmanim_str = ''
    if zmanim_dict['zmanim']['sunset'] == 'X:XX:XX':
        if lang == 'Русский':
            zmanim_str = 'В данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            zmanim_str = 'In these latitudes it is impossible to determine' \
                         ' because of polar night/day'
        return zmanim_str
    elif zmanim_dict['zmanim']['tzeis_595_degrees'] == 'X:XX:XX'\
            and zmanim_dict['zmanim']['tzeis_850_degrees'] == 'X:XX:XX':
        d3 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_shema_gra'],
                               "%H:%M:%S")
        d4 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                               "%H:%M:%S")
        d5 = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                               "%H:%M:%S")
        # высчитываем полночь, прибавляя 12 часов
        d_delta = timedelta(hours=12)
        d6 = d5 + d_delta

        chazot_laila = str(datetime.time(d6))
        shaa_zman_gra = str(d4 - d3)  # астрономический час по арго

        chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))
        if lang == 'Русский':
            zmanim_str = '*Расширенные зманим*\n\n' \
                         '*Еврейская дата:* {} {} {}\n' \
                         '*Рассвет* _(Алот Ашахар)_ *—* {:.5s}\n' \
                         '*Самое раннее время надевания ' \
                         'талита и тфилин* _(Мишеякир)_ *—* {:.5s}\n' \
                         '*Восход солнца* _(Нец Ахама)_ *—* {:.5s}\n' \
                         '*Конец времени чтения Шма [АГРО]* *—* {:.5s}\n' \
                         '*Конец времени чтения' \
                         ' молитвы Амида [АГРО]* *—* {:.5s}\n' \
                         '*Полдень* _(Хацот)_ *—* {:.5s}\n' \
                         '*Самое раннее время Минхи*' \
                         ' _(Минха Гдола)_ *—* {:.5s}\n' \
                         '*Малая Минха* _(Минха Ктана)_ *—* {:.5s}\n' \
                         '*Полу-Минха* _(Плаг Минха)_ *—* {:.5s}\n' \
                         '*Заход солнца* _(Шкия)_ *—* {:.5s}\n' \
                         '*Выход звезд [42 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [595 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [72 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Полночь* _(Хацот Алайла)_ *—* {:.5s}\n\n' \
                         '*Астрономический час [АГРО]* *—* {:.4s}' \
                .format(year_day[0],
                        data.jewish_months_a[month],
                        year_day[1],
                        alot_chazot_time,
                        alot_chazot_time,
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        chazot_laila,
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        chazot_laila, shaa_zman_gra)
        elif lang == 'English':
            zmanim_str = '*Extended Zmanim*\n\n*Hebrew date:* {} {} {}\n' \
                         '*Alot Hashachar* *—* {:.5s}\n' \
                         '*Misheyakir* *—* {:.5s}\n' \
                         '*Hanetz Hachama* *—* {:.5s}\n' \
                         '*Sof Zman Shema [GR"A]* *—* {:.5s}\n' \
                         '*Sof Zman Tefilah [GR"A]* *—* {:.5s}\n' \
                         '*Chatzot Hayom* *—* {:.5s}\n' \
                         '*Mincha Gedolah* *—* {:.5s}\n' \
                         '*Mincha Ketanah* *—* {:.5s}\n' \
                         '*Plag Mincha* *—* {:.5s}\n' \
                         '*Shkiat Hachama* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [42 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [595 degrees]* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [72 minutes]*  *—* {:.5s}\n' \
                         '*Chatzot Halayiah* *—* {:.5s}\n\n' \
                         '*Astronomical Hour [GR"A]* *—* {:.4s}' \
                .format(year_day[0],
                        month,
                        year_day[1],
                        alot_chazot_time,
                        alot_chazot_time,
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        chazot_laila,
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        chazot_laila, shaa_zman_gra)
    elif zmanim_dict['zmanim']['tzeis_850_degrees'] == 'X:XX:XX':
        d3 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_shema_gra'],
                               "%H:%M:%S")
        d4 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                               "%H:%M:%S")
        d5 = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                               "%H:%M:%S")
        # высчитываем полночь, прибавляя 12 часов
        d_delta = timedelta(hours=12)
        d6 = d5 + d_delta

        chazot_laila = str(datetime.time(d6))
        shaa_zman_gra = str(d4 - d3)  # астрономический час по арго

        chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))
        if lang == 'Русский':
            zmanim_str = '*Расширенные зманим*\n\n' \
                         '*Еврейская дата:* {} {} {}\n' \
                         '*Рассвет* _(Алот Ашахар)_ *—* {:.5s}\n' \
                         '*Самое раннее время надевания ' \
                         'талита и тфилин* _(Мишеякир)_ *—* {:.5s}\n' \
                         '*Восход солнца* _(Нец Ахама)_ *—* {:.5s}\n' \
                         '*Конец времени чтения Шма [АГРО]* *—* {:.5s}\n' \
                         '*Конец времени чтения' \
                         ' молитвы Амида [АГРО]* *—* {:.5s}\n' \
                         '*Полдень* _(Хацот)_ *—* {:.5s}\n' \
                         '*Самое раннее время Минхи*' \
                         ' _(Минха Гдола)_ *—* {:.5s}\n' \
                         '*Малая Минха* _(Минха Ктана)_ *—* {:.5s}\n' \
                         '*Полу-Минха* _(Плаг Минха)_ *—* {:.5s}\n' \
                         '*Заход солнца* _(Шкия)_ *—* {:.5s}\n' \
                         '*Выход звезд [42 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [595 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [72 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Полночь* _(Хацот Алайла)_ *—* {:.5s}\n\n' \
                         '*Астрономический час [АГРО]* *—* {:.4s}' \
                .format(year_day[0],
                        data.jewish_months_a[month],
                        year_day[1],
                        alot_chazot_time,
                        alot_chazot_time,
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        chazot_laila, shaa_zman_gra)
        elif lang == 'English':
            zmanim_str = '*Extended Zmanim*\n\n*Hebrew date:* {} {} {}\n' \
                         '*Alot Hashachar* *—* {:.5s}\n' \
                         '*Misheyakir* *—* {:.5s}\n' \
                         '*Hanetz Hachama* *—* {:.5s}\n' \
                         '*Sof Zman Shema [GR"A]* *—* {:.5s}\n' \
                         '*Sof Zman Tefilah [GR"A]* *—* {:.5s}\n' \
                         '*Chatzot Hayom* *—* {:.5s}\n' \
                         '*Mincha Gedolah* *—* {:.5s}\n' \
                         '*Mincha Ketanah* *—* {:.5s}\n' \
                         '*Plag Mincha* *—* {:.5s}\n' \
                         '*Shkiat Hachama* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [42 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [595 degrees]* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [72 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [850 degrees]* *—* {:.5s}\n' \
                         '*Chatzot Halayiah* *—* {:.5s}\n\n' \
                         '*Astronomical Hour [GR"A]* *—* {:.4s}' \
                .format(year_day[0],
                        month,
                        year_day[1],
                        zmanim_dict['zmanim']['alos_ma'],
                        zmanim_dict['zmanim']['talis_ma'],
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        zmanim_dict['zmanim']['tzeis_850_degrees'],
                        chazot_laila, shaa_zman_gra)
    elif zmanim_dict['zmanim']['sof_zman_shema_ma'] == 'X:XX:XX'\
            or zmanim_dict['zmanim']['sof_zman_tefila_ma'] == 'X:XX:XX':
        d3 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_shema_gra'],
                               "%H:%M:%S")
        d4 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                               "%H:%M:%S")
        d5 = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                               "%H:%M:%S")
        # высчитываем полночь, прибавляя 12 часов
        d_delta = timedelta(hours=12)
        d6 = d5 + d_delta

        chazot_laila = str(datetime.time(d6))
        shaa_zman_gra = str(d4 - d3)  # астрономический час по арго
        if zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX'\
                and zmanim_dict['zmanim']['talis_ma'] == 'X:XX:XX':
            chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                            "%H:%M:%S")
            chazot_delta = timedelta(hours=12)
            alot_delta = chazot_time - chazot_delta
            alot_chazot_time = str(datetime.time(alot_delta))
            zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
            zmanim_dict['zmanim']['talis_ma'] = alot_chazot_time
        elif zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX':
            chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                            "%H:%M:%S")
            chazot_delta = timedelta(hours=12)
            alot_delta = chazot_time - chazot_delta
            alot_chazot_time = str(datetime.time(alot_delta))
            zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
        if lang == 'Русский':
            zmanim_str = '*Расширенные зманим*\n\n' \
                         '*Еврейская дата:* {} {} {}\n' \
                         '*Рассвет* _(Алот Ашахар)_ *—* {:.5s}\n' \
                         '*Самое раннее время надевания ' \
                         'талита и тфилин* _(Мишеякир)_ *—* {:.5s}\n' \
                         '*Восход солнца* _(Нец Ахама)_ *—* {:.5s}\n' \
                         '*Конец времени чтения Шма [АГРО]* *—* {:.5s}\n' \
                         '*Конец времени чтения' \
                         ' молитвы Амида [АГРО]* *—* {:.5s}\n' \
                         '*Полдень* _(Хацот)_ *—* {:.5s}\n' \
                         '*Самое раннее время Минхи*' \
                         ' _(Минха Гдола)_ *—* {:.5s}\n' \
                         '*Малая Минха* _(Минха Ктана)_ *—* {:.5s}\n' \
                         '*Полу-Минха* _(Плаг Минха)_ *—* {:.5s}\n' \
                         '*Заход солнца* _(Шкия)_ *—* {:.5s}\n' \
                         '*Выход звезд [42 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [595 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [72 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [850 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Полночь* _(Хацот Алайла)_ *—* {:.5s}\n\n' \
                         '*Астрономический час [АГРО]* *—* {:.4s}' \
                .format(year_day[0],
                        data.jewish_months_a[month],
                        year_day[1],
                        zmanim_dict['zmanim']['alos_ma'],
                        zmanim_dict['zmanim']['talis_ma'],
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        zmanim_dict['zmanim']['tzeis_850_degrees'],
                        chazot_laila, shaa_zman_gra)
        elif lang == 'English':
            zmanim_str = '*Extended Zmanim*\n\n*Hebrew date:* {} {} {}\n' \
                         '*Alot Hashachar* *—* {:.5s}\n' \
                         '*Misheyakir* *—* {:.5s}\n' \
                         '*Hanetz Hachama* *—* {:.5s}\n' \
                         '*Sof Zman Shema [GR"A]* *—* {:.5s}\n' \
                         '*Sof Zman Tefilah [GR"A]* *—* {:.5s}\n' \
                         '*Chatzot Hayom* *—* {:.5s}\n' \
                         '*Mincha Gedolah* *—* {:.5s}\n' \
                         '*Mincha Ketanah* *—* {:.5s}\n' \
                         '*Plag Mincha* *—* {:.5s}\n' \
                         '*Shkiat Hachama* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [42 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [595 degrees]* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [72 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [850 degrees]* *—* {:.5s}\n' \
                         '*Chatzot Halayiah* *—* {:.5s}\n\n' \
                         '*Astronomical Hour [GR"A]* *—* {:.4s}' \
                .format(year_day[0],
                        month,
                        year_day[1],
                        zmanim_dict['zmanim']['alos_ma'],
                        zmanim_dict['zmanim']['talis_ma'],
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        zmanim_dict['zmanim']['tzeis_850_degrees'],
                        chazot_laila, shaa_zman_gra)

    else:
        # блок вычисления времени
        d1 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_shema_ma'],
                               "%H:%M:%S")
        d2 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_tefila_ma'],
                               "%H:%M:%S")
        d3 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_shema_gra'],
                               "%H:%M:%S")
        d4 = datetime.strptime(zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                               "%H:%M:%S")
        d5 = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                               "%H:%M:%S")
        # высчитываем полночь, прибавляя 12 часов
        d_delta = timedelta(hours=12)
        d6 = d5 + d_delta

        chazot_laila = str(datetime.time(d6))
        shaa_zman_ma = str(d2 - d1)  # астрономический час по маген авраам
        shaa_zman_gra = str(d4 - d3)  # астрономический час по арго
        if zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX'\
                and zmanim_dict['zmanim']['talis_ma'] == 'X:XX:XX':
            chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                            "%H:%M:%S")
            chazot_delta = timedelta(hours=12)
            alot_delta = chazot_time - chazot_delta
            alot_chazot_time = str(datetime.time(alot_delta))
            zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
            zmanim_dict['zmanim']['talis_ma'] = alot_chazot_time
        elif zmanim_dict['zmanim']['alos_ma'] == 'X:XX:XX':
            chazot_time = datetime.strptime(zmanim_dict['zmanim']['chatzos'],
                                            "%H:%M:%S")

            chazot_delta = timedelta(hours=12)
            alot_delta = chazot_time - chazot_delta
            alot_chazot_time = str(datetime.time(alot_delta))
            zmanim_dict['zmanim']['alos_ma'] = alot_chazot_time
        if lang == 'Русский':
            zmanim_str = '*Расширенные зманим*\n\n' \
                         '*Еврейская дата:* {} {} {}\n' \
                         '*Рассвет* _(Алот Ашахар)_ *—* {:.5s}\n' \
                         '*Самое раннее время надевания ' \
                         'талита и тфилин* _(Мишеякир)_ *—* {:.5s}\n' \
                         '*Восход солнца* _(Нец Ахама)_ *—* {:.5s}\n' \
                         '*Конец времени чтения Шма' \
                         ' [Маген Авраам]* *—* {:.5s}\n' \
                         '*Конец времени чтения Шма [АГРО]* *—* {:.5s}\n' \
                         '*Конец времени чтения молитвы Амида\n' \
                         '[Маген Авраам]* *—*  {:.5s}\n' \
                         '*Конец времени чтения' \
                         ' молитвы Амида [АГРО]* *—* {:.5s}\n' \
                         '*Полдень* _(Хацот)_ *—* {:.5s}\n' \
                         '*Самое раннее время Минхи*' \
                         ' _(Минха Гдола)_ *—* {:.5s}\n' \
                         '*Малая Минха* _(Минха Ктана)_ *—* {:.5s}\n' \
                         '*Полу-Минха* _(Плаг Минха)_ *—* {:.5s}\n' \
                         '*Заход солнца* _(Шкия)_ *—* {:.5s}\n' \
                         '*Выход звезд [42 минуты]*' \
                         ' _(Цет Акохавим)_  *—* {:.5s}\n' \
                         '*Выход звезд [595 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [72 минуты]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Выход звезд [850 градусов]*' \
                         ' _(Цет Акохавим)_ *—* {:.5s}\n' \
                         '*Полночь* _(Хацот Алайла)_ *—* {:.5s}\n\n' \
                         '*Астрономический час [Маген Авраам]* *—*  {:.4s}\n' \
                         '*Астрономический час [АГРО]* *—* {:.4s}' \
                .format(year_day[0],
                        data.jewish_months_a[month],
                        year_day[1],
                        zmanim_dict['zmanim']['alos_ma'],
                        zmanim_dict['zmanim']['talis_ma'],
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_ma'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_ma'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        zmanim_dict['zmanim']['tzeis_850_degrees'],
                        chazot_laila, shaa_zman_ma, shaa_zman_gra)
        elif lang == 'English':
            zmanim_str = '*Extended Zmanim*\n\n*Hebrew date:* {} {} {}\n' \
                         '*Alot Hashachar* *—* {:.5s}\n' \
                         '*Misheyakir* *—* {:.5s}\n' \
                         '*Hanetz Hachama* *—* {:.5s}\n' \
                         '*Sof Zman Shema [M"A]* *—* {:.5s}\n' \
                         '*Sof Zman Shema [GR"A]* *—* {:.5s}\n' \
                         '*Sof Zman Tefilah [M"A]* *—* {:.5s}\n' \
                         '*Sof Zman Tefilah [GR"A]* *—* {:.5s}\n' \
                         '*Chatzot Hayom* *—* {:.5s}\n' \
                         '*Mincha Gedolah* *—* {:.5s}\n' \
                         '*Mincha Ketanah* *—* {:.5s}\n' \
                         '*Plag Mincha* *—* {:.5s}\n' \
                         '*Shkiat Hachama* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [42 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [595 degrees]* *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [72 minutes]*  *—* {:.5s}\n' \
                         '*Tzeit Hakochavim [850 degrees]* *—* {:.5s}\n' \
                         '*Chatzot Halayiah* *—* {:.5s}\n\n' \
                         '*Astronomical Hour [M"A]* *—* {:.4s}\n' \
                         '*Astronomical Hour [GR"A]* *—* {:.4s}' \
                .format(year_day[0],
                        month,
                        year_day[1],
                        zmanim_dict['zmanim']['alos_ma'],
                        zmanim_dict['zmanim']['talis_ma'],
                        zmanim_dict['zmanim']['sunrise'],
                        zmanim_dict['zmanim']['sof_zman_shema_ma'],
                        zmanim_dict['zmanim']['sof_zman_shema_gra'],
                        zmanim_dict['zmanim']['sof_zman_tefila_ma'],
                        zmanim_dict['zmanim']['sof_zman_tefila_gra'],
                        zmanim_dict['zmanim']['chatzos'],
                        zmanim_dict['zmanim']['mincha_gedola_ma'],
                        zmanim_dict['zmanim']['mincha_ketana_gra'],
                        zmanim_dict['zmanim']['plag_mincha_ma'],
                        zmanim_dict['zmanim']['sunset'],
                        zmanim_dict['zmanim']['tzeis_42_minutes'],
                        zmanim_dict['zmanim']['tzeis_595_degrees'],
                        zmanim_dict['zmanim']['tzeis_72_minutes'],
                        zmanim_dict['zmanim']['tzeis_850_degrees'],
                        chazot_laila, shaa_zman_ma, shaa_zman_gra)

    return zmanim_str


if __name__ == '__main__':
    pass
