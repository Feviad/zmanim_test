import requests
import pytz
import data
import functions as f
from datetime import datetime


URL = 'http://db.ou.org/zmanim/getCalendarData.php'


def get_daf(loc, lang):
    tz = f.get_tz_by_location(loc)
    tz_time = pytz.timezone(tz)
    now = datetime.now(tz_time)
    params = {'mode': 'day',
              'timezone': tz,
              'dateBegin': f'{now.month}/{now.day}/{now.year}',
              'lat': loc[0],
              'lng': loc[1]
              }
    daf = requests.get(URL, params=params)
    daf_dict = daf.json()
    if lang == 'Русский':
        daf_str = f'*Даф Йоми*\n\n📗 *Трактат:*' \
                  f' {data.talmud[daf_dict["dafYomi"]["masechta"]]}' \
                  f'\n📄 *Лист:* {daf_dict["dafYomi"]["daf"]}'
    elif lang == 'English':
        daf_str = f'*Daf Yomi*\n\n📗 *Masechta:* ' \
                  f'{daf_dict["dafYomi"]["masechta"]}\n' \
                  f'📄 *Daf:* {daf_dict["dafYomi"]["daf"]}'
    return daf_str
