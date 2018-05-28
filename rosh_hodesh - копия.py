import requests
import calendar
import re
import pytz
import data
import functions as f
from datetime import datetime
from pyluach import dates


URL = 'http://db.ou.org/zmanim/getHolidayCalData.php'


def get_chodesh_dict(hebrew_date, params):
    chodesh = requests.get(URL, params=params)
    chodesh_dicts = chodesh.json()
    month = hebrew_date[1]
    if month == 6:
        next_year = hebrew_date[0] + 1
        params = {'hebrewYear': next_year}
        molad_next_year = requests.get(URL, params=params)
        new_chodesh_dicts = molad_next_year.json()
        chodesh_dict = new_chodesh_dicts[6]
    elif len(chodesh_dicts) == 13:  # если год високосный
        if month < 13:  # если первые 12 месяцев
            chodesh_dict = chodesh_dicts[month]
        else:  # если адар II
            chodesh_dict = chodesh_dicts[0]  # выбираем в нем нисан
    else:  # если год не високосный — дальше так же
        if month < 12:
            chodesh_dict = chodesh_dicts[month]
        else:
            chodesh_dict = chodesh_dicts[0]
    return chodesh_dict


def get_month_name(chodesh_dict):
    # парсим название месяца
    month = re.findall(r'[a-zA-z]+', chodesh_dict['JewishMonth'])
    if len(month) == 2:
        month_str = f'{month[0]} {month[1]}'
    else:
        month_str = f'{month[0]}'
    return month_str


def get_rh_lenght(hebrew_date):
    # получаем длинну ТЕКУЩЕГО еврейского месяца чтоб определить длинну РХ
    month_days = dates.HebrewDate._month_length(hebrew_date[0], hebrew_date[1])
    if month_days == 30:
        return 2
    else:
        return 1


def get_rh_date_and_day(hebrew_date, lenght, lang):
    # определяем число дней в месяце:
    month_days = dates.HebrewDate._month_length(hebrew_date[0], hebrew_date[1])
    # определяем дату последнего дня месяца
    last_month_day = dates.HebrewDate(hebrew_date[0],
                                      hebrew_date[1],
                                      month_days
                                      ).to_greg().tuple()
    # определяем длинну рош ходеша
    if lenght == 2:
        # проверка на случай если два дня РХ в разных месяцах гр. календаря
        first_day = last_month_day[2]
        month_length = calendar.monthrange(last_month_day[0],
                                           last_month_day[1]
                                           )[1]
        if first_day == month_length:
            if last_month_day[1] == 12:  # проверка на случай если это декабрь
                if lang == 'Русский':
                    rh_days = '31 декабря {} года и 1 января {} года'.format(
                        last_month_day[0],
                        last_month_day[0] + 1
                    )
                elif lang == 'English':
                    rh_days = '31 December {} and 1 January {}'.format(
                        last_month_day[0],
                        last_month_day[0] + 1
                    )
                # определяем день недели
                day_of_week_id = calendar.weekday(
                    last_month_day[0],
                    12,
                    31
                )
                if lang == 'Русский':
                    day_of_week = '{}-{}'.format(
                        data.days_r[day_of_week_id],
                        data.days_r[day_of_week_id + 1]
                    )
                elif lang == 'English':
                    day_of_week = '{}-{}'.format(
                        data.days_e[day_of_week_id],
                        data.days_e[day_of_week_id + 1]
                    )
            else:
                if lang == 'Русский':
                    rh_days = '{} и 1 {} и {} {} года'.format(
                        first_day,
                        data.gr_months_index[last_month_day[1]],
                        data.gr_months_index[last_month_day[1] + 1],
                        last_month_day[0]
                    )
                elif lang == 'English':
                    rh_days = '{} and 1 {} and {} {}'.format(
                        first_day,
                        data.gr_months_index_en[last_month_day[1]],
                        data.gr_months_index_en[last_month_day[1] + 1],
                        last_month_day[0]
                    )
                # определяем день недели
                day_of_week_id = calendar.weekday(
                    last_month_day[0],
                    last_month_day[1],
                    first_day
                )
                if lang == 'Русский':
                    day_of_week = '{}-{}'.format(
                        data.days_r[day_of_week_id],
                        data.days_r[day_of_week_id + 1]
                    )
                elif lang == 'English':
                    day_of_week = '{}-{}'.format(
                        data.days_e[day_of_week_id],
                        data.days_e[day_of_week_id + 1]
                    )
        else:
            if lang == 'Русский':
                rh_days = '{} и {} {} {} года'.format(
                    first_day,
                    first_day + 1,
                    data.gr_months_index[last_month_day[1]],
                    last_month_day[0]
                )
            elif lang == 'English':
                rh_days = '{} and {} {} {}'.format(
                    first_day,
                    first_day + 1,
                    data.gr_months_index_en[last_month_day[1]],
                    last_month_day[0]
                )
            # определяем день недели
            day_of_week_id = calendar.weekday(
                last_month_day[0],
                last_month_day[1],
                first_day
            )
            if lang == 'Русский':
                day_of_week = '{}-{}'.format(
                    data.days_r[day_of_week_id],
                    data.days_r[day_of_week_id + 1]
                )
            elif lang == 'English':
                day_of_week = '{}-{}'.format(
                    data.days_e[day_of_week_id],
                    data.days_e[day_of_week_id + 1]
                )
    else:
        # проверка на то, является ли число перед рх последним днем гр месяца
        month_length = calendar.monthrange(
            last_month_day[0],
            last_month_day[1]
        )[1]
        if last_month_day[2] == month_length:
            # проверка, является ли это декабрь
            if last_month_day[1] == 12:
                if lang == 'Русский':
                    rh_days = '1 января {} года'.format(last_month_day[0] + 1)
                elif lang == 'English':
                    rh_days = '1 January {}'.format(last_month_day[0] + 1)
                # определяем день недели
                day_of_week_id = calendar.weekday(
                    last_month_day[0] + 1,
                    1,
                    1
                )
                if lang == 'Русский':
                    day_of_week = data.days_r[day_of_week_id]
                elif lang == 'English':
                    day_of_week = data.days_e[day_of_week_id]
            else:
                if lang == 'Русский':
                    rh_days = '1 {} {} года'.format(
                        data.gr_months_index[last_month_day[1] + 1],
                        last_month_day[0]
                    )
                elif lang == 'English':
                    rh_days = '1 {} {}'.format(
                        data.gr_months_index_en[last_month_day[1] + 1],
                        last_month_day[0]
                    )
                # определяем день недели
                day_of_week_id = calendar.weekday(
                    last_month_day[0],
                    last_month_day[1] + 1,
                    1
                )
                if lang == 'Русский':
                    day_of_week = data.days_r[day_of_week_id]
                elif lang == 'English':
                    day_of_week = data.days_e[day_of_week_id]
        else:
            if lang == 'Русский':
                rh_days = '{} {} {} года'.format(
                    last_month_day[2] + 1,
                    data.gr_months_index[last_month_day[1]],
                    last_month_day[0]
                )
            elif lang == 'English':
                rh_days = '{} {} {}'.format(
                    last_month_day[2] + 1,
                    data.gr_months_index_en[last_month_day[1]],
                    last_month_day[0]
                )
            # определяем день недели
            day_of_week_id = calendar.weekday(
                last_month_day[0],
                last_month_day[1],
                last_month_day[2] + 1)
            if lang == 'Русский':
                day_of_week = data.days_r[day_of_week_id]
            elif lang == 'English':
                day_of_week = data.days_e[day_of_week_id]
    return '{}, {}'.format(rh_days, day_of_week)


def get_molad(chodesh_dict, lang):
    # парсим название месяца
    molad_month = re.search(r'[a-zA-z]+', chodesh_dict['EnglishDate']).group(0)
    # парсим число молада
    molad_day = re.search(r'\d+', chodesh_dict['EnglishDate']).group(0)
    # парсим числа для молада — часы, минуты, части
    molad_numbers = re.findall(r'\d+', chodesh_dict['Molad'])
    # парсим день недели молада
    day_of_week = re.search(r'[a-zA-z]+', chodesh_dict['DayOfWeek']).group(0)

    if lang == 'Русский':
        molad = '{day} {month}, {day_of_week}, {nhours} {hours}, ' \
                '{nmins} {mins} и {nchalakim} {chalakin}' \
            .format(day=molad_day,
                    month=data.gr_months[molad_month],
                    day_of_week=data.gr_dayofweek[day_of_week],
                    nhours=molad_numbers[0],
                    hours=data.hours.get(molad_numbers[0][-1:], 'часов'),
                    nmins=molad_numbers[1],
                    mins=data.minutes.get(molad_numbers[1][-1:], 'минут'),
                    nchalakim=molad_numbers[2],
                    chalakin=data.chalakim.get(molad_numbers[2], 'частей')
                    )
    elif lang == 'English':
        molad = '{day} {month}, {day_of_week}, {nhours} {hours}, ' \
                '{nmins} {mins} and {nchalakim} {chalak}' \
            .format(day=molad_day,
                    month=molad_month,
                    day_of_week=day_of_week,
                    nhours=molad_numbers[0],
                    hours=data.hours_e.get(molad_numbers[0], 'hours'),
                    nmins=molad_numbers[1],
                    mins=data.minutes_e.get(molad_numbers[1], 'minutes'),
                    nchalakim=molad_numbers[2],
                    chalak=data.chalakim_e.get(molad_numbers[2], 'chalakim')
                    )
    return molad


def get_rh(loc, lang):
    tz = f.get_tz_by_location(loc)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    hebrew_date = dates.GregorianDate(now.year,
                                      now.month, now.day).to_heb().tuple()

    # проверка на рош ашану
    if hebrew_date[1] == 6:
        hebrew_date = (
            hebrew_date[0],
            hebrew_date[1] + 1,
            hebrew_date[2]
        )
    params = {'hebrewYear': hebrew_date[0]}
    chodesh_dict = get_chodesh_dict(hebrew_date, params)
    length_of_rh = get_rh_lenght(hebrew_date)
    length_str = f'{length_of_rh}'

    if lang == 'Русский':
        rh = '*Рош ходеш* 🌒\n\n' \
             '*Месяц:* {month}\n' \
             '*Продолжительность Рош Ходеша:* {length} {length_r}\n' \
             '*Рош Ходеш:* {rh}\n' \
             '*Молад:* {mol}'.format(
                month=data.jewish_months[get_month_name(chodesh_dict)],
                length=length_str,
                length_r=data.length_r[length_str],
                rh=get_rh_date_and_day(hebrew_date, length_of_rh, lang),
                mol=get_molad(chodesh_dict, lang)
             )
    elif lang == 'English':
        rh = '*Rosh Chodesh* 🌒\n\n*Month:* {month}\n' \
             '*Rosh Chodesh duration:* {length} {length_r}\n' \
             '*Rosh Chodesh:* {rh}\n' \
             '*Molad:* {mol}'.format(
                month=get_month_name(chodesh_dict),
                length=length_str,
                length_r=data.length_e[length_str],
                rh=get_rh_date_and_day(hebrew_date, length_of_rh, lang),
                mol=get_molad(chodesh_dict, lang)
             )
    return rh
