# -*- coding: utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta
import pytz
import re
import data
import functions as f

URL_Hol = 'http://db.ou.org/zmanim/getHolidayCalData.php'
URL_Cal = 'http://db.ou.org/zmanim/getCalendarData.php'

sess = requests.Session()
sess.mount(URL_Cal, HTTPAdapter(max_retries=5))


def send_request(param, url=URL_Cal):
    response = sess.get(url, params=param)
    return response


# Получаем словарь , index - индекс в общем json'е
def get_holidays_dict(holi_index, holi_id):
    tz = f.get_tz_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    if tz in ['Asia/Jerusalem', 'Asia/Tel_Aviv', 'Asia/Hebron']:
        params = {'year': year,
                  'israelHolidays': 'true'
                  }
    else:
        params = {'year': year}

    holidays = send_request(params, URL_Hol)

    holidays_dicts = holidays.json()
    holidays_dict = holidays_dicts[holi_index]
    if month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
            or holidays_dict['name'] == 'Chanukah':
        params = {'year': year - 1}
        holidays = send_request(params, URL_Hol)
        holidays_dicts = holidays.json()
        holidays_dict = holidays_dicts[holi_index]
        h_numbers = re.findall(r'\d+', holidays_dict['dateYear1'])
        brackets = re.findall(r'[(){}[\]]+', holidays_dict['dateYear1'])
        if brackets and int(h_numbers[1]) > int(day) \
                and holidays_dict['name'] == 'Chanukah' \
                or brackets and holidays_dict['name'] == 'AsarahBTevet' \
                and int(h_numbers[0]) > int(day):
            params = {'year': year - 1}
            holidays = send_request(params, URL_Hol)
            holidays_dicts = holidays.json()
            holidays_dict = holidays_dicts[holi_index]
        else:
            params = {'year': year}
            holidays = send_request(params, URL_Hol)
            holidays_dicts = holidays.json()
            holidays_dict = holidays_dicts[holi_index]

    return holidays_dict


# Парсим название праздника/поста, чтобы перевести его
def get_holiday_name(holidays_dict, lang):
    holiday = re.findall(r'[a-zA-z]+', holidays_dict['name'])
    name = ''
    if lang == 'Русский':
        name = str(data.holidays_name[str(holiday[0])])
    elif lang == 'English':
        name = str(data.holidays_name_en[str(holiday[0])])

    return name


# Получаем данные по празднику
def get_holiday_data(holidays_dict, holi_id, lang):
    tz = f.get_tz_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    h_numbers = re.findall(r'\d+', holidays_dict['dateYear1'])
    d_m = re.findall(r'[a-zA-z]+', holidays_dict['dateYear1'])
    h_numbers_2 = re.findall(r'\d+', holidays_dict['dateYear2'])
    d_m_2 = re.findall(r'[a-zA-z]+', holidays_dict['dateYear2'])
    brackets = re.findall(r'[(){}[\]]+', holidays_dict['dateYear1'])
    holiday_number = ''
    if len(d_m) == 4 or len(d_m_2) == 4:
        day2 = h_numbers[1]
        month2 = data.holi_month_index[d_m[3]]
        if brackets:
            month2 = 13
        if holidays_dict['name'] in ['Pesach', 'Chanukah']:
            if d_m_2[1] == d_m_2[3]:
                if int(month2) == int(month) and int(day2) < int(day) \
                        or int(month2) < int(month):
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year + 1}, ' \
                                         f'{data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
                        or month == 1 and holidays_dict['name'] == 'Chanukah':
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month2 == 13:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
                else:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
            else:
                if int(month2) == int(month) and int(day2) < int(day) \
                        or int(month2) < int(month):
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
                        or month == 1 and holidays_dict['name'] == 'Chanukah':
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]}-' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month2 == 13:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
                else:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]}-' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
        else:
            if d_m_2[1] == d_m_2[3]:
                if int(month2) == int(month) and int(day2) < int(day) \
                        or int(month2) < int(month):
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]} и ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]} and ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
                        or month == 1 and holidays_dict['name'] == 'Chanukah':
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]} и ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]} and ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month2 == 13:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]} и ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]} and ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
                else:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]} и ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]} and ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
            else:
                if int(month2) == int(month) and int(day2) < int(day) \
                        or int(month2) < int(month):
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]} и ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]} and ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
                        or month == 1 and holidays_dict['name'] == 'Chanukah':
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers_2[0]} и ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month[d_m_2[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7[d_m_2[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers_2[0]} and ' \
                                         f'{h_numbers_2[1]}' \
                                         f' {data.holi_month_en[d_m_2[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m_2[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m_2[2]]}'
                elif month2 == 13:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]} и ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year + 1} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]} and ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year + 1},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'
                else:
                    if lang == 'Русский':
                        holiday_number = f'📅 Дата: {h_numbers[0]} и ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month[d_m[3]]}' \
                                         f' {year} годa,' \
                                         f' {data.hdays_of_7[d_m[0]]}-' \
                                         f'{data.hdays_of_7[d_m[2]]}'
                    elif lang == 'English':
                        holiday_number = f'📅 Date: {h_numbers[0]} and ' \
                                         f'{h_numbers[1]}' \
                                         f' {data.holi_month_en[d_m[3]]}' \
                                         f' {year},' \
                                         f' {data.hdays_of_7_en[d_m[0]]}-' \
                                         f'{data.hdays_of_7_en[d_m[2]]}'

    else:
        day1 = h_numbers[0]
        month1 = data.holi_month_index[d_m[1]]
        if brackets:
            month1 = 13
        if int(month1) < int(month) or int(month1) == int(month) \
                and int(day) > int(day1):
            if lang == 'Русский':
                holiday_number = f'📅 Дата: {h_numbers_2[0]}' \
                                 f' {data.holi_month[d_m_2[1]]}' \
                                 f' {year + 1} годa,' \
                                 f' {data.hdays_of_7[d_m_2[0]]}'
            elif lang == 'English':
                holiday_number = f'📅 Date: {h_numbers_2[0]}' \
                                 f' {data.holi_month_en[d_m_2[1]]}' \
                                 f' {year + 1},' \
                                 f' {data.hdays_of_7_en[d_m_2[0]]}'
        elif month == 1 and holidays_dict['name'] == 'AsarahBTevet' \
                or holidays_dict['name'] == 'Chanukah':
            if lang == 'Русский':
                holiday_number = f'📅 Дата: {h_numbers_2[0]}' \
                                 f' {data.holi_month[d_m_2[1]]}' \
                                 f' {year} годa,' \
                                 f' {data.hdays_of_7[d_m_2[0]]}'
            elif lang == 'English':
                holiday_number = f'📅 Date: {h_numbers_2[0]}' \
                                 f' {data.holi_month_en[d_m_2[1]]}' \
                                 f' {year},' \
                                 f' {data.hdays_of_7_en[d_m_2[0]]}'
        elif month1 == 13:
            if lang == 'Русский':
                holiday_number = f'📅 Дата: {h_numbers[0]}' \
                                 f' {data.holi_month[d_m[1]]}' \
                                 f' {year + 1} годa,' \
                                 f' {data.hdays_of_7[d_m[0]]}'
            elif lang == 'English':
                holiday_number = f'📅 Date: {h_numbers[0]}' \
                                 f' {data.holi_month_en[d_m[1]]}' \
                                 f' {year + 1},' \
                                 f' {data.hdays_of_7_en[d_m[0]]}'
        else:
            if lang == 'Русский':
                holiday_number = f'📅 Дата: {h_numbers[0]}' \
                                 f' {data.holi_month[d_m[1]]}' \
                                 f' {year} годa,' \
                                 f' {data.hdays_of_7[d_m[0]]}'
            elif lang == 'English':
                holiday_number = f'📅 Date: {h_numbers[0]}' \
                                 f' {data.holi_month_en[d_m[1]]}' \
                                 f' {year},' \
                                 f' {data.hdays_of_7_en[d_m[0]]}'

    return holiday_number


# Начало и конец поста
def fast(get_dict, holi_id, lang):
    loc = f.get_location_by_id(holi_id)
    tz = f.get_tz_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    h_numbers = re.findall(r'\d+', get_dict['dateYear1'])
    d_m = re.findall(r'[a-zA-z]+', get_dict['dateYear1'])
    h_numbers_2 = re.findall(r'\d+', get_dict['dateYear2'])
    d_m_2 = re.findall(r'[a-zA-z]+', get_dict['dateYear2'])
    brackets = re.findall(r'[(){}[\]]+', get_dict['dateYear1'])

    month_time = data.holi_month_index[d_m[1]]
    if brackets:
        month_time = 13
    if int(month_time) < int(month) or int(month_time) == int(month) \
            and int(h_numbers[0]) < int(day):
        month_time = data.holi_month_index[d_m_2[1]]
        day_time = h_numbers_2[0]
    else:
        day_time = h_numbers[0]
        month_time = data.holi_month_index[d_m[1]]
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{month_time}/{day_time}/{year}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'
              }
    holiday_time = send_request(params)

    holi_time_dict = holiday_time.json()
    fast_time = ''
    if holi_time_dict['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            fast_time = '\nВ данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            fast_time = '\nIn these latitudes zmanim is impossible' \
                        ' to determine because of polar night/day'
        return fast_time
    earlier_time = datetime.strptime(holi_time_dict['zmanim']['sunset'],
                                     "%H:%M:%S")
    earlier_delta = timedelta(minutes=31)
    earlier_delta2 = timedelta(minutes=28)
    earlier_delta3 = timedelta(minutes=25)
    sefer_ben_ashmashot = str(datetime.time(earlier_time + earlier_delta))
    nevareshet = str(datetime.time(earlier_time + earlier_delta2))
    shmirat_shabat = str(datetime.time(earlier_time + earlier_delta3))
    if holi_time_dict['zmanim']['alos_ma'] == 'X:XX:XX':
        chazot_time = datetime.strptime(holi_time_dict['zmanim']['chatzos'],
                                        "%H:%M:%S")
        chazot_delta = timedelta(hours=12)
        alot_delta = chazot_time - chazot_delta
        alot_chazot_time = str(datetime.time(alot_delta))
        holi_time_dict['zmanim']['alos_ma'] = alot_chazot_time
    if get_dict['name'] == 'TishaBAv':
        delta = timedelta(days=1)
        date1 = datetime.strptime(f'{month_time}/{day_time}/{year}',
                                  '%m/%d/%Y')
        d1 = (date1 - delta).strftime('%Y-%m-%d').lstrip("0").replace("-0",
                                                                      "-")
        spec_date = re.findall(r'\d+', str(d1))
        params = {'mode': 'day',
                  'timezone': tz,
                  'dateBegin': f'{spec_date[1]}/{spec_date[2]}/{spec_date[0]}',
                  'lat': loc[0],
                  'lng': loc[1],
                  'havdala_offset': '72'}
        holiday_time_av = send_request(params)
        holi_time_dict_av = holiday_time_av.json()
        if lang == 'Русский':
            fast_time = 'Начало поста {}' \
                        ' {}:' \
                        ' *{:.5s}*\nХацот: *{:.5s}*\n' \
                        'Конец поста {}' \
                        ' {}\n' \
                        '✨ Выход звезд:' \
                        ' *{:.5s}*\n' \
                        '🕖 Сефер бен Ашмашот: *{:.5s}*\n' \
                        '🕘 Неварешет: *{:.5s}*\n' \
                        '🕑 Шмират шаббат килхата: *{:.5s}*' \
                .format(spec_date[2],
                        data.gr_months_index[str(spec_date[1])],
                        holi_time_dict_av["zmanim"]["sunset"],
                        holi_time_dict_av["zmanim"]["chatzos"],
                        day_time, data.gr_months_index[month_time],
                        holi_time_dict["zmanim"]["tzeis_595_degrees"],
                        sefer_ben_ashmashot, nevareshet, shmirat_shabat)
        elif lang == 'English':
            fast_time = 'Fast begins {}' \
                        ' {}:' \
                        ' *{:.5s}*\nChatzot: *{:.5s}*\n' \
                        'The fast ends {}' \
                        ' {}\n' \
                        '✨ Tzeit akohavim:' \
                        ' *{:.5s}*\n' \
                        '🕖 Sefer ben Ashmashot: *{:.5s}*\n' \
                        '🕘 Nevareshet: *{:.5s}*\n' \
                        '🕑 Shmirat shabbat kelhata: *{:.5s}*' \
                .format(spec_date[2],
                        data.gr_months_index_en[str(spec_date[1])],
                        holi_time_dict_av["zmanim"]["sunset"],
                        holi_time_dict_av["zmanim"]["chatzos"],
                        day_time, data.gr_months_index_en[month_time],
                        holi_time_dict["zmanim"]["tzeis_595_degrees"],
                        sefer_ben_ashmashot, nevareshet, shmirat_shabat)
    else:
        if lang == 'Русский':
            fast_time = 'Начало поста {}' \
                        ' {}:' \
                        ' *{:.5s}*\n' \
                        'Конец поста {}' \
                        ' {}\n' \
                        '✨ Выход звезд:' \
                        ' *{:.5s}*\n' \
                        '🕖 Сефер бен Ашмашот: *{:.5s}*\n' \
                        '🕘 Неварешет: *{:.5s}*\n' \
                        '🕑 Шмират шаббат килхата: *{:.5s}*' \
                .format(day_time,
                        data.gr_months_index[month_time],
                        holi_time_dict["zmanim"]["alos_ma"],
                        day_time, data.gr_months_index[month_time],
                        holi_time_dict["zmanim"]["tzeis_595_degrees"],
                        sefer_ben_ashmashot, nevareshet, shmirat_shabat)
        elif lang == 'English':
            fast_time = 'The fast begins {}' \
                        ' {}:' \
                        ' *{:.5s}*\n' \
                        'Fast ends {}' \
                        ' {}\n' \
                        '✨ Tzeit akohavim:' \
                        ' *{:.5s}*\n' \
                        '🕖 Sefer ben Ashmashot: *{:.5s}*\n' \
                        '🕘 Nevareshet: *{:.5s}*\n' \
                        '🕑 Shmirat shabbat kelhata: *{:.5s}*' \
                .format(day_time,
                        data.gr_months_index_en[month_time],
                        holi_time_dict["zmanim"]["alos_ma"],
                        day_time, data.gr_months_index_en[month_time],
                        holi_time_dict["zmanim"]["tzeis_595_degrees"],
                        sefer_ben_ashmashot, nevareshet, shmirat_shabat)
    return fast_time


# Время зажигания и Авдолы Рош-Ашана, Шавуота
def rosh_ash(get_dict, holi_id, lang):
    tz = f.get_tz_by_id(holi_id)
    loc = f.get_location_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    h_numbers = re.findall(r'\d+', get_dict['dateYear1'])
    d_m = re.findall(r'[a-zA-z]+', get_dict['dateYear1'])
    h_numbers_2 = re.findall(r'\d+', get_dict['dateYear2'])
    d_m_2 = re.findall(r'[a-zA-z]+', get_dict['dateYear2'])

    month_time = data.holi_month_index[d_m[1]]
    if month_time < month or month_time == month \
            and int(h_numbers[0]) < int(day):
        month_time = data.holi_month_index[d_m_2[1]]
        day_time = h_numbers_2[0]
    else:
        day_time = h_numbers[0]
        month_time = data.holi_month_index[d_m[1]]

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{month_time}/{day_time}/{year}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time = send_request(params)

    holi_time_dict = holiday_time.json()
    ra_time = ''
    if holi_time_dict['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            ra_time = '\nВ данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            ra_time = '\nIn these latitudes zmanim is impossible' \
                        ' to determine because of polar night/day'
        return ra_time
    date1 = datetime.strptime(f'{month_time}/{day_time}/{year}', '%m/%d/%Y')
    delta1 = timedelta(days=1)
    delta2 = timedelta(days=2)
    d1 = (date1 - delta1).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    d2 = (date1 + delta1).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    d3 = (date1 + delta2).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    spec_date1 = re.findall(r'\d+', str(d1))
    spec_date2 = re.findall(r'\d+', str(d2))
    spec_date3 = re.findall(r'\d+', str(d3))

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date1[1]}/{spec_date1[2]}/{spec_date1[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra1 = send_request(params)

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date2[1]}/{spec_date2[2]}/{spec_date2[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra2 = send_request(params)

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date3[1]}/{spec_date3[2]}/{spec_date3[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra3 = send_request(params)

    holi_time_dict_ra1 = holiday_time_ra1.json()
    holi_time_dict_ra2 = holiday_time_ra2.json()
    holi_time_dict_ra3 = holiday_time_ra3.json()
    if holi_time_dict_ra1['zmanim']['chatzos'] == 'X:XX:XX'\
            or holi_time_dict_ra2['zmanim']['chatzos'] == 'X:XX:XX'\
            or holi_time_dict_ra3['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            ra_time = '\nВ данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            ra_time = '\nIn these latitudes zmanim is impossible' \
                        ' to determine because of polar night/day'
        return ra_time
    d_candle = datetime.strptime(holi_time_dict_ra1['zmanim']['sunset'],
                                 "%H:%M:%S")
    d_candle2 = datetime.strptime(holi_time_dict_ra2['zmanim']['sunset'],
                                  "%H:%M:%S")
    d_delta = timedelta(minutes=18)
    if holi_time_dict['dayOfWeek'] == '4':
        if lang == 'Русский':
            ra_time = '🕯 Зажигание свечей {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Зажигание свечей {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Зажигание свечей (Шаббат) {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '✨ Авдала {}' \
                      ' {}:' \
                      ' *{:.5s}*' \
                .format(spec_date1[2],
                        data.gr_months_index[str(spec_date1[1])],
                        str(datetime.time(d_candle - d_delta)), day_time,
                        data.gr_months_index[month_time],
                        holi_time_dict["zmanim"]["tzeis_850_degrees"],
                        spec_date2[2],
                        data.gr_months_index[str(spec_date2[1])],
                        str(datetime.time(d_candle2 - d_delta)),
                        spec_date3[2],
                        data.gr_months_index[str(spec_date3[1])],
                        holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
        elif lang == 'English':
            ra_time = '🕯 Candle lighting {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Candle lighting {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Candle lighting {}' \
                      ' {}: ' \
                      '*{:.5s}*\n' \
                      '✨ Avdala {}' \
                      ' {}:' \
                      ' *{:.5s}*' \
                .format(spec_date1[2],
                        data.gr_months_index_en[str(spec_date1[1])],
                        str(datetime.time(d_candle - d_delta)), day_time,
                        data.gr_months_index_en[month_time],
                        holi_time_dict["zmanim"]["tzeis_850_degrees"],
                        spec_date2[2],
                        data.gr_months_index_en[str(spec_date2[1])],
                        str(datetime.time(d_candle2 - d_delta)),
                        spec_date3[2],
                        data.gr_months_index_en[str(spec_date3[1])],
                        holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
    else:
        if lang == 'Русский':
            ra_time = '🕯 Зажигание свечей {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Зажигание свечей {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '✨ Авдала {}' \
                      ' {}:' \
                      ' *{:.5s}*' \
                .format(spec_date1[2],
                        data.gr_months_index[str(spec_date1[1])],
                        str(datetime.time(d_candle - d_delta)), day_time,
                        data.gr_months_index[month_time],
                        holi_time_dict["zmanim"]["tzeis_850_degrees"],
                        spec_date2[2],
                        data.gr_months_index[str(spec_date2[1])],
                        holi_time_dict_ra2["zmanim"]["tzeis_850_degrees"])
        elif lang == 'English':
            ra_time = '🕯 Candle lighting {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '🕯 Candle lighting {}' \
                      ' {}:' \
                      ' *{:.5s}*\n' \
                      '✨ Avdala {}' \
                      ' {}:' \
                      ' *{:.5s}*' \
                .format(spec_date1[2],
                        data.gr_months_index_en[str(spec_date1[1])],
                        str(datetime.time(d_candle - d_delta)), day_time,
                        data.gr_months_index_en[month_time],
                        holi_time_dict["zmanim"]["tzeis_850_degrees"],
                        spec_date2[2],
                        data.gr_months_index_en[str(spec_date2[1])],
                        holi_time_dict_ra2["zmanim"]["tzeis_850_degrees"])

    return ra_time


# Время зажигания и Авдолы Йом-Кипура
def yom_kippurim(get_dict, holi_id, lang):
    loc = f.get_location_by_id(holi_id)
    tz = f.get_tz_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    h_numbers = re.findall(r'\d+', get_dict['dateYear1'])
    d_m = re.findall(r'[a-zA-z]+', get_dict['dateYear1'])
    h_numbers_2 = re.findall(r'\d+', get_dict['dateYear2'])
    d_m_2 = re.findall(r'[a-zA-z]+', get_dict['dateYear2'])

    month_time = data.holi_month_index[d_m[1]]
    if month_time < month or month_time == month \
            and int(h_numbers[0]) < int(day):
        month_time = data.holi_month_index[d_m_2[1]]
        day_time = h_numbers_2[0]
    else:
        day_time = h_numbers[0]
        month_time = data.holi_month_index[d_m[1]]

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{month_time}/{day_time}/{year}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time = send_request(params)
    holi_time_dict = holiday_time.json()
    fast_time = ''
    if holi_time_dict['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            fast_time = '\nВ данных широтах невозможно определить' \
                         ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            fast_time = '\nIn these latitudes zmanim is impossible' \
                        ' to determine because of polar night/day'
        return fast_time
    delta = timedelta(days=1)
    date1 = datetime.strptime(f'{month_time}/{day_time}/{year}', '%m/%d/%Y')
    d1 = (date1 - delta).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    spec_date = re.findall(r'\d+', str(d1))

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date[1]}/{spec_date[2]}/{spec_date[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_candle = send_request(params)
    holi_time_dict_candle = holiday_time_candle.json()

    d1 = datetime.strptime(holi_time_dict_candle['zmanim']['sunset'],
                           "%H:%M:%S")
    d_delta = timedelta(minutes=18)
    if lang == 'Русский':
        fast_time = '🕯 Зажигание свечей и начало поста {}' \
                    ' {}:' \
                    ' *{:.5s}*\n' \
                    '✨ Авдала и конец поста {}' \
                    ' {}:' \
                    ' *{:.5s}*' \
            .format(spec_date[2], data.gr_months_index[str(spec_date[1])],
                    str(datetime.time(d1 - d_delta)), day_time,
                    data.gr_months_index[month_time],
                    holi_time_dict["zmanim"]["tzeis_850_degrees"])
    elif lang == 'English':
        fast_time = '🕯 Candle lighting and the fast begins {}' \
                    ' {}:' \
                    ' *{:.5s}*\n' \
                    '✨ Avdala and the fast ends {}' \
                    ' {}:' \
                    ' *{:.5s}*' \
            .format(spec_date[2], data.gr_months_index_en[str(spec_date[1])],
                    str(datetime.time(d1 - d_delta)), day_time,
                    data.gr_months_index_en[month_time],
                    holi_time_dict["zmanim"]["tzeis_850_degrees"])

    return fast_time


# Время зажигания и Авдолы Пейсаха и Суккота
def sukkot_pesach_shavout(get_dict, number, holi_id, lang):
    loc = f.get_location_by_id(holi_id)
    tz = f.get_tz_by_id(holi_id)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    year = now.year
    month = now.month
    day = now.day

    israel = False
    if tz == 'Asia/Jerusalem' or tz == 'Asia/Tel_Aviv' or tz == 'Asia/Hebron':
        israel = True
    h_numbers = re.findall(r'\d+', get_dict['dateYear1'])
    d_m = re.findall(r'[a-zA-z]+', get_dict['dateYear1'])
    h_numbers_2 = re.findall(r'\d+', get_dict['dateYear2'])
    d_m_2 = re.findall(r'[a-zA-z]+', get_dict['dateYear2'])
    if get_dict['name'] == 'Pesach':
        month_time = data.holi_month_index[d_m[3]]
    else:
        month_time = data.holi_month_index[d_m[1]]
    day_time = ''
    if number == 1:
        if month_time < month or month_time == month \
                and int(h_numbers[1]) < int(day):
            month_time = data.holi_month_index[d_m_2[1]]
            day_time = h_numbers_2[0]
        else:
            day_time = h_numbers[0]
            month_time = data.holi_month_index[d_m[1]]
    elif number == 2:
        if month_time < month or month_time == month \
                and int(h_numbers[1]) < int(day):
            month_time = data.holi_month_index[d_m_2[3]]
            day_time = h_numbers_2[1]
        else:
            day_time = h_numbers[1]
            month_time = data.holi_month_index[d_m[3]]

    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{month_time}/{day_time}/{year}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time = send_request(params)

    holi_time_dict = holiday_time.json()
    ra_time = ''
    if holi_time_dict['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            ra_time = '\nВ данных широтах невозможно определить' \
                      ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            ra_time = '\nIn these latitudes zmanim is impossible' \
                      ' to determine because of polar night/day'
        return ra_time
    date1 = datetime.strptime(f'{month_time}/{day_time}/{year}', '%m/%d/%Y')
    delta1 = timedelta(days=1)
    delta2 = timedelta(days=2)
    d1 = (date1 - delta1).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    d2 = (date1 + delta1).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    d3 = (date1 + delta2).strftime('%Y-%m-%d').lstrip("0").replace("-0", "-")
    spec_date1 = re.findall(r'\d+', str(d1))
    spec_date2 = re.findall(r'\d+', str(d2))
    spec_date3 = re.findall(r'\d+', str(d3))
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date1[1]}/{spec_date1[2]}/{spec_date1[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra1 = send_request(params)
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date2[1]}/{spec_date2[2]}/{spec_date2[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra2 = send_request(params)
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{spec_date3[1]}/{spec_date3[2]}/{spec_date3[0]}',
              'lat': loc[0],
              'lng': loc[1],
              'havdala_offset': '72'}
    holiday_time_ra3 = send_request(params)
    holi_time_dict_ra1 = holiday_time_ra1.json()
    holi_time_dict_ra2 = holiday_time_ra2.json()
    holi_time_dict_ra3 = holiday_time_ra3.json()
    if holi_time_dict_ra1['zmanim']['chatzos'] == 'X:XX:XX'\
            or holi_time_dict_ra2['zmanim']['chatzos'] == 'X:XX:XX'\
            or holi_time_dict_ra3['zmanim']['chatzos'] == 'X:XX:XX':
        if lang == 'Русский':
            ra_time = '\nВ данных широтах невозможно определить' \
                      ' зманим из-за полярного дня/полярной ночи'
        elif lang == 'English':
            ra_time = '\nIn these latitudes zmanim is impossible' \
                      ' to determine because of polar night/day'
        return ra_time
    d_candle = datetime.strptime(holi_time_dict_ra1['zmanim']['sunset'],
                                 "%H:%M:%S")
    d_candle2 = datetime.strptime(holi_time_dict_ra2['zmanim']['sunset'],
                                  "%H:%M:%S")
    d_delta = timedelta(minutes=18)
    # проверка на израиль
    if not israel:
        if holi_time_dict['dayOfWeek'] == '4':
            if lang == 'Русский':
                ra_time = '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Зажигание свечей (Шаббат) {}' \
                          ' {}: ' \
                          '*{:.5s}*\n' \
                          '✨ Авдала {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time,
                            data.gr_months_index[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"],
                            spec_date2[2],
                            data.gr_months_index[str(spec_date2[1])],
                            str(datetime.time(d_candle2 - d_delta)),
                            spec_date3[2],
                            data.gr_months_index[str(spec_date3[1])],
                            holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
            elif lang == 'English':
                ra_time = '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Candle lighting {}' \
                          ' {}: ' \
                          '*{:.5s}*\n' \
                          '✨ Avdala {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index_en[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time,
                            data.gr_months_index_en[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"],
                            spec_date2[2],
                            data.gr_months_index_en[str(spec_date2[1])],
                            str(datetime.time(d_candle2 - d_delta)),
                            spec_date3[2],
                            data.gr_months_index_en[str(spec_date3[1])],
                            holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
        else:
            if lang == 'Русский':
                ra_time = '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '✨ Авдала {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"],
                            spec_date2[2],
                            data.gr_months_index[str(spec_date2[1])],
                            holi_time_dict_ra2["zmanim"]["tzeis_850_degrees"])
            elif lang == 'English':
                ra_time = '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '✨ Avdala {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index_en[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index_en[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"],
                            spec_date2[2],
                            data.gr_months_index_en[str(spec_date2[1])],
                            holi_time_dict_ra2["zmanim"]["tzeis_850_degrees"])
    else:
        if holi_time_dict['dayOfWeek'] == '5':
            if lang == 'Русский':
                ra_time = '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Зажигание свечей (Шаббат) {} {}: *{:.5s}*\n' \
                          '✨ Авдала {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index[month_time],
                            str(datetime.time(d_candle2 - d_delta)),
                            spec_date2[2],
                            data.gr_months_index[str(spec_date2[1])],
                            holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
            elif lang == 'English':
                ra_time = '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '🕯 Candle lighting {} {}: *{:.5s}*\n' \
                          '✨ Avdala {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index_en[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index_en[month_time],
                            str(datetime.time(d_candle2 - d_delta)),
                            spec_date2[2],
                            data.gr_months_index_en[str(spec_date2[1])],
                            holi_time_dict_ra3["zmanim"]["tzeis_850_degrees"])
        else:
            if lang == 'Русский':
                ra_time = '🕯 Зажигание свечей {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '✨ Авдала {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"])
            elif lang == 'English':
                ra_time = '🕯 Candle lighting {}' \
                          ' {}:' \
                          ' *{:.5s}*\n' \
                          '✨ Avdala {}' \
                          ' {}:' \
                          ' *{:.5s}*' \
                    .format(spec_date1[2],
                            data.gr_months_index_en[str(spec_date1[1])],
                            str(datetime.time(d_candle - d_delta)),
                            day_time, data.gr_months_index_en[month_time],
                            holi_time_dict["zmanim"]["tzeis_850_degrees"])

    return ra_time


index = get_holidays_dict


def tu_bshevat(holi_id, lang):
    ind = index(0, holi_id)
    tu_bshevat_name = get_holiday_name(ind, lang)
    tu_bshevat_date = get_holiday_data(ind, holi_id, lang)
    tu_bshevat_str = f'*{tu_bshevat_name}* 🌳\n' \
                     f'{tu_bshevat_date}'
    return tu_bshevat_str


def taanit_esther(holi_id, lang):
    ind = index(1, holi_id)
    taanit_esther_name = get_holiday_name(ind, lang)
    taanit_esther_date = get_holiday_data(ind, holi_id, lang)
    taanit_esther_time = fast(ind, holi_id, lang)
    taanit_esther_str = f'*{taanit_esther_name}*\n\n' \
                        f'{taanit_esther_date}\n' \
                        f'{taanit_esther_time}'
    return taanit_esther_str


def purim(holi_id, lang):
    ind_0 = index(2, holi_id)
    ind_1 = index(3, holi_id)
    purim_name = get_holiday_name(ind_0, lang)
    purim_date = get_holiday_data(ind_0, holi_id, lang)
    shushan_purim_name = get_holiday_name(ind_1, lang)
    shushan_purim_date = get_holiday_data(ind_1, holi_id, lang)
    purim_str = f'*{purim_name}* 🎭\n' \
                f'{purim_date}\n\n' \
                f'*{shushan_purim_name}*\n' \
                f'{shushan_purim_date}'
    return purim_str


def pesach(holi_id, lang):
    ind = index(4, holi_id)
    pesach_name = get_holiday_name(ind, lang)
    pesach_date = get_holiday_data(ind, holi_id, lang)
    pesach_time = sukkot_pesach_shavout(ind, 1, holi_id, lang)
    pesach_time2 = sukkot_pesach_shavout(ind, 2, holi_id, lang)
    pesach_str = f'*{pesach_name}* 🍷🍷🍷🍷\n\n' \
                 f'{pesach_date}\n' \
                 f'{pesach_time}\n\n' \
                 f'{pesach_time2}'
    return pesach_str


def get_israel(holi_id, lang):
    ind_0 = index(5, holi_id)
    ind_1 = index(6, holi_id)
    ind_2 = index(7, holi_id)
    ind_3 = index(9, holi_id)
    yom_hashoah_name = get_holiday_name(ind_0, lang)
    yom_hashoah_date = get_holiday_data(ind_0, holi_id, lang)
    yom_hazikaron_name = get_holiday_name(ind_1, lang)
    yom_hazikaron_date = get_holiday_data(ind_1, holi_id, lang)
    yom_haatzmaut_name = get_holiday_name(ind_2, lang)
    yom_haatzmaut_date = get_holiday_data(ind_2, holi_id, lang)
    yom_yerushalayim_name = get_holiday_name(ind_3, lang)
    yom_yerushalayim_date = get_holiday_data(ind_3, holi_id, lang)
    israel_str = f'🇮🇱🇮🇱🇮🇱\n' \
                 f'*{yom_hashoah_name}*\n' \
                 f'{yom_hashoah_date}\n\n' \
                 f'*{yom_hazikaron_name}*\n' \
                 f'{yom_hazikaron_date}\n\n' \
                 f'*{yom_haatzmaut_name}*\n' \
                 f'{yom_haatzmaut_date}\n\n' \
                 f'*{yom_yerushalayim_name}*\n' \
                 f'{yom_yerushalayim_date}'
    return israel_str


def lag_baomer(holi_id, lang):
    ind = index(8, holi_id)
    lag_baomer_name = get_holiday_name(ind, lang)
    lag_baomer_date = get_holiday_data(ind, holi_id, lang)
    lag_baomer_str = f'*{lag_baomer_name}* 🔥🏹\n' \
                     f'{lag_baomer_date}'
    return lag_baomer_str


def shavuot(holi_id, lang):
    ind = index(10, holi_id)
    shavuot_name = get_holiday_name(ind, lang)
    shavuot_date = get_holiday_data(ind, holi_id, lang)
    shavuot_time = sukkot_pesach_shavout(ind, 1, holi_id, lang)
    shavuot_str = f'*{shavuot_name}* 🌄🍶\n\n' \
                  f'{shavuot_date}\n' \
                  f'{shavuot_time}'
    return shavuot_str


def shiva_asar_tammuz(holi_id, lang):
    ind = index(11, holi_id)
    shiva_asar_tammuz_name = get_holiday_name(ind, lang)
    shiva_asar_tammuz_date = get_holiday_data(ind, holi_id, lang)
    shiva_asar_tammuz_time = fast(ind, holi_id, lang)
    shiva_asar_tammuz_str = f'*{shiva_asar_tammuz_name}*\n\n' \
                            f'{shiva_asar_tammuz_date}\n' \
                            f'{shiva_asar_tammuz_time}'
    return shiva_asar_tammuz_str


def tisha_bav(holi_id, lang):
    ind = index(12, holi_id)
    tisha_bav_name = get_holiday_name(ind, lang)
    tisha_bav_date = get_holiday_data(ind, holi_id, lang)
    tisha_bav_time = fast(ind, holi_id, lang)
    tisha_bav_str = f'*{tisha_bav_name}*\n\n' \
                    f'{tisha_bav_date}\n' \
                    f'{tisha_bav_time}'
    return tisha_bav_str


def tu_bav(holi_id, lang):
    ind = index(13, holi_id)
    tu_bav_name = get_holiday_name(ind, lang)
    tu_bav_date = get_holiday_data(ind, holi_id, lang)
    tu_bav_str = f'*{tu_bav_name}* 💑\n' \
                 f'{tu_bav_date}'
    return tu_bav_str


def rosh_hashanah(holi_id, lang):
    ind = index(14, holi_id)
    rosh_hashanah_name = get_holiday_name(ind, lang)
    rosh_date = get_holiday_data(ind, holi_id, lang)
    rosh_time = rosh_ash(ind, holi_id, lang)
    rosh_hashanah_str = f'*{rosh_hashanah_name}* 🍯🍎\n\n' \
                        f'{rosh_date}\n' \
                        f'{rosh_time}'
    return rosh_hashanah_str


def tzom_gedaliah(holi_id, lang):
    ind = index(15, holi_id)
    tzom_gedaliah_name = get_holiday_name(ind, lang)
    tzom_gedaliah_date = get_holiday_data(ind, holi_id, lang)
    tzom_gedaliah_time = fast(ind, holi_id, lang)
    tzom_gedaliah_str = f'*{tzom_gedaliah_name}*\n\n' \
                        f'{tzom_gedaliah_date}\n' \
                        f'{tzom_gedaliah_time}'
    return tzom_gedaliah_str


def yom_kipur(holi_id, lang):
    ind = index(16, holi_id)
    yom_kippur_name = get_holiday_name(ind, lang)
    yom_kippur_date = get_holiday_data(ind, holi_id, lang)
    yom_kippur_time = yom_kippurim(ind, holi_id, lang)
    yom_kippur_str = f'*{yom_kippur_name}* 🕍\n\n' \
                     f'{yom_kippur_date}\n' \
                     f'{yom_kippur_time}'
    return yom_kippur_str


def succos(holi_id, lang):
    ind_0 = index(17, holi_id)
    ind_1 = index(21, holi_id)
    ind_2 = index(18, holi_id)
    succos_name = get_holiday_name(ind_0, lang)
    succos_date = get_holiday_data(ind_0, holi_id, lang)
    succos_time = sukkot_pesach_shavout(ind_1, 1, holi_id, lang)
    hoshana_rabba_name = get_holiday_name(ind_2, lang)
    hoshana_rabba_date = get_holiday_data(ind_2, holi_id, lang)
    if hoshana_rabba_name == 'HoshanaRabba':
        succos_str = f'*{succos_name}* 🌿🌴🍋\n\n' \
                     f'{succos_date}\n' \
                     f'{succos_time}\n\n' \
                     f'*Hoshana Rabba*\n' \
                     f'{hoshana_rabba_date}'
    else:
        succos_str = f'*{succos_name}* 🌿🌴🍋\n\n' \
                     f'{succos_date}\n' \
                     f'{succos_time}\n\n' \
                     f'*{hoshana_rabba_name}*\n' \
                     f'{hoshana_rabba_date}'
    return succos_str


def shmini_atzeres_simhat(holi_id, lang):
    tz = f.get_tz_by_id(holi_id)
    ind_0 = index(19, holi_id)
    ind_1 = index(20, holi_id)
    shmini_atzeres_simhat_name = get_holiday_name(ind_0, lang)
    shmini_atzeres_simhat_date = get_holiday_data(ind_0, holi_id, lang)
    simhat_torah_name = get_holiday_name(ind_1, lang)
    simhat_torah_date = get_holiday_data(ind_1, holi_id, lang)
    shmini_simhat_time = sukkot_pesach_shavout(ind_0, 1, holi_id, lang)
    if tz in ['Asia/Jerusalem', 'Asia/Tel_Aviv', 'Asia/Hebron']:
        if lang == 'Русский':
            shmini_simhat_str = f'*{shmini_atzeres_simhat_name}' \
                                f' и Симхат Тора* \n' \
                                f'{shmini_atzeres_simhat_date}\n\n' \
                                f'{shmini_simhat_time}'
        if lang == 'English':
            shmini_simhat_str = f'*{shmini_atzeres_simhat_name}' \
                                f' и Simhat Torah* \n' \
                                f'{shmini_atzeres_simhat_date}\n\n' \
                                f'{shmini_simhat_time}'
    else:
        shmini_simhat_str = f'*{shmini_atzeres_simhat_name},' \
                            f' {simhat_torah_name}*\n\n' \
                            f'{shmini_atzeres_simhat_date}\n' \
                            f'{simhat_torah_date}\n\n' \
                            f'{shmini_simhat_time}'
    return shmini_simhat_str


def chanukah(holi_id, lang):
    ind = index(22, holi_id)
    chanukah_name = get_holiday_name(ind, lang)
    chanukah_date = get_holiday_data(ind, holi_id, lang)
    chanukah_str = f'*{chanukah_name}* 🕎\n' \
                   f'{chanukah_date}'
    return chanukah_str


def asarah_btevet(holi_id, lang):
    ind = index(23, holi_id)
    asarah_btevet_name = get_holiday_name(ind, lang)
    asarah_btevet_date = get_holiday_data(ind, holi_id, lang)
    asarah_btevet_time = fast(ind, holi_id, lang)
    asarah_btevet_str = f'*{asarah_btevet_name}*\n\n' \
                        f'{asarah_btevet_date}\n' \
                        f'{asarah_btevet_time}'
    return asarah_btevet_str
