# -*- coding: utf-8 -*-
import telebot
import redis
import lang as l
import data
import zmanim
import shabbos
import rosh_hodesh
import daf
import functions as f
import holidays as h
from telebot import types


def zmanim_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = zmanim.get_zmanim(user, 'Русский')
        return response


def zmanim_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = zmanim.get_zmanim(user, 'English')
        return response


def ext_zmanim_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = zmanim.get_ext_zmanim(loc, 'Русский')
        return response


def ext_zmanim_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = zmanim.get_ext_zmanim(loc, 'English')
        return response


def shabbat_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = shabbos.get_shabbos_string(loc, 'Русский')
        return response


def shabbat_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = shabbos.get_shabbos_string(loc, 'English')
        return response


def rosh_chodesh_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = rosh_hodesh.get_rh(loc, 'Русский')
        return response


def rosh_chodesh_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = rosh_hodesh.get_rh(loc, 'English')
        return response


def holidays_ru(user):
    response = 'Выберите: (клавиатуру можно скроллить)'
    holiday_menu = f.get_holiday_menu('Русский')
    return response, holiday_menu


def holidays_en(user):
    response = 'Choose: (scroll keyboard)'
    holiday_menu = f.get_holiday_menu('English')
    return response, holiday_menu


def fasts_ru(user):
    response = 'Выберите:'
    fast_menu = f.get_fast_menu('Русский')
    return response, fast_menu


def fasts_en(user):
    response = 'Choose:'
    fast_menu = f.get_fast_menu('English')
    return response, fast_menu


def daf_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = daf.get_daf(loc, 'Русский')
        return response


def daf_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = daf.get_daf(loc, 'English')
        return response


def update_location_ru(user):
    geobutton = types.ReplyKeyboardMarkup(True)
    geobutton.row(types.KeyboardButton(request_location=True,
                                       text='Отправить новые координаты'))
    geobutton.row('Отмена')
    response = 'Пожалуйста, предоставьте новые координаты, ' \
               'нажав на кнопку.\n*Внимание*! Telegram на ПК пока что не ' \
               'поддерживает отправку координат таким методом. Чтобы ' \
               'отправить координаты с ПК, отправьте их в текстовом виде ' \
               'через запятую, например "_55.5, 37.7_", либо перешлите сюда ' \
               'сообщение с геометкой.'
    return response, geobutton


def update_location_en(user):
    geobutton = types.ReplyKeyboardMarkup(True)
    geobutton.row(types.KeyboardButton(request_location=True,
                                       text='Update location'))
    geobutton.row('Cancel')
    response = 'Please, send new location by tapping the button.\n' \
               '*Notice* that Telegram on PC is not supported yet ' \
               'sending locations in this way. In order to send location on ' \
               'PC, send it like text, for example, "_55.5, 37.7_", or ' \
               'forward message with location here.'
    return response, geobutton


def russian(user):
    l.set_lang(user, 'Русский')
    return main_menu(user)


def english(user):
    l.set_lang(user, 'English')
    return main_menu(user)


def main_menu(user):
    r = redis.StrictRedis()
    lang_in_redis = r.get(f'{user}')
    if not lang_in_redis:
        lang_in_db = l.get_lang_by_id(user)
        if not lang_in_db:
            return change_lang(user)
        else:
            r.set(f'{user}', data.lang[lang_in_db])
            r.expire(f'{user}', 31536000)
            lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]
    else:
        lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]

    auth = f.get_location_by_id(user)
    if not auth:
        resp_and_markup = request_location(user)
        response = resp_and_markup[0]
        user_markup = resp_and_markup[1]
    else:
        user_markup = f.get_main_menu(lang)
        if lang == 'Русский':
            response = 'Выберите:'
        elif lang == 'English':
            response = 'Choose:'
    return response, user_markup


def request_location(user):
    r = redis.StrictRedis()
    lang_in_redis = r.get(f'{user}')
    if not lang_in_redis:
        lang_in_db = l.get_lang_by_id(user)
        if not lang_in_db:
            return change_lang(user)
        else:
            r.set(f'{user}', data.lang[lang_in_db])
            r.expire(f'{user}', 31536000)
            lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]
    else:
        lang = data.short_lang[r.get(f'{user}').decode('unicode_escape')]

    geobutton = types.ReplyKeyboardMarkup(True)
    if lang == 'Русский':
        response = 'Пожалуйста, предоставьте ваши координаты, ' \
                   'нажав на кнопку.\n*Внимание*! Telegram на ПК пока что не ' \
                   'поддерживает отправку координат таким методом. Чтобы ' \
                   'отправить координаты с ПК, отправьте их в текстовом виде '\
                   'через запятую, например "_55.5, 37.7_", либо перешлите сюда'\
                   ' сообщение с геометкой.'
        geobutton.row(types.KeyboardButton(request_location=True,
                                           text='Отправить местоположение'))
    elif lang == 'English':
        response = 'Please, send your location by tapping the button.\n' \
                   '*Notice* that Telegram on PC is not supported yet ' \
                   'sending locations in this way. In order to send location '\
                   'on PC, send it like text, for example, "_55.5, 37.7_", or ' \
                   'forward message with location here.'
        geobutton.row(types.KeyboardButton(request_location=True,
                                           text='Send location'))



    return response, geobutton


def faq_ru(user):
    response = 'https://goo.gl/bavHuO'
    return response


def faq_en(user):
    response = 'https://goo.gl/4320iu'
    return response


def report_ru(user):
    response = 'Чтобы сообщить об ошибке, пожалуйста, напишите одному из нас: \n' \
               't.me/benyomin \nt.me/Meir_Yartzev\n' \
               't.me/APJIAC \n' \
               'Пожалуйста, убедитесь, что вы ознакомились с часто ' \
               'задаваемыми вопросами, доступными по кнопке "ЧаВо" '
    return [response]


def report_en(user):
    response = 'For bug report please write to one of us: \nt.me/benyomin ' \
               '\nt.me/Meir_Yartzev \nt.me/APJIAC\nPlease, make sure that you ' \
               'had been read F.A.Q. available by "F.A.Q." button'
    return [response]


def rosh_hashana_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.rosh_hashanah(user, 'Русский')
        return response


def rosh_hashana_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.rosh_hashanah(user, 'English')
        return response


def yom_kippur_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.yom_kipur(user, 'Русский')
        return response


def yom_kippur_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.yom_kipur(user, 'English')
        return response


def succot_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.succos(user, 'Русский')
        return response


def succot_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.succos(user, 'English')
        return response


def shmini_atzeret_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shmini_atzeres_simhat(user, 'Русский')
        return response


def shmini_atzeret_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shmini_atzeres_simhat(user, 'English')
        return response


def chanukah_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.chanukah(user, 'Русский')
        return response


def chanukah_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.chanukah(user, 'English')
        return response


def tu_beshvat_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tu_bshevat(user, 'Русский')
        return response


def tu_beshvat_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tu_bshevat(user, 'English')
        return response


def purim_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.purim(user, 'Русский')
        return response


def purim_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.purim(user, 'English')
        return response


def pesach_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.pesach(user, 'Русский')
        return response


def pesach_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.pesach(user, 'English')
        return response


def lag_baomer_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.lag_baomer(user, 'Русский')
        return response


def lag_baomer_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.lag_baomer(user, 'English')
        return response


def shavuot_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shavuot(user, 'Русский')
        return response


def shavuot_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shavuot(user, 'English')
        return response


def tu_beav_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tu_bav(user, 'Русский')
        return response


def tu_beav_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tu_bav(user, 'English')
        return response


def israel_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.get_israel(user, 'Русский')
        return response


def israel_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.get_israel(user, 'English')
        return response


def fast_gedaliah_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tzom_gedaliah(user, 'Русский')
        return response


def fast_gedaliah_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tzom_gedaliah(user, 'English')
        return response


def asarah_betevet_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.asarah_btevet(user, 'Русский')
        return response


def asarah_betevet_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.asarah_btevet(user, 'English')
        return response


def fast_esthet_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.taanit_esther(user, 'Русский')
        return response


def fast_esther_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.taanit_esther(user, 'English')
        return response


def sheva_asar_betammuz_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shiva_asar_tammuz(user, 'Русский')
        return response


def sheva_asar_betammuz_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.shiva_asar_tammuz(user, 'English')
        return response


def tisha_beav_ru(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tisha_bav(user, 'Русский')
        return response


def tisha_beav_en(user):
    loc = f.get_location_by_id(user)
    if not loc:
        return request_location(user)
    else:
        response = h.tisha_bav(user, 'English')
        return response


def change_lang(user):
    response = 'Выберите язык/Choose the language'
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Русский', 'English')
    return response, user_markup


def incorrect_text(user):
    lang = l.get_lang_grom_redis(user)
    if lang == 'Русский':
        response = 'Некорректная команда. Пожалуйста, выберите один из ' \
                   'вариантов на кнопках.'
    elif lang == 'English':
        response = 'Incorrect command. Please, choose one of the options on' \
                   ' the buttons'
    return response


def make_response(command, user, bot):
    commands = {'Сменить язык'           : change_lang,
                'Language'        : change_lang,
                'Отмена'                 : main_menu,
                'Cancel'                 : main_menu,
                'Русский'                : russian,
                'English'                : english,
                'Назад/Back'             : change_lang,
                'Зманим'                 : zmanim_ru,
                'Zmanim'                 : zmanim_en,
                'Расширенные Зманим'     : ext_zmanim_ru,
                'Extended Zmanim'        : ext_zmanim_en,
                'Шаббат'                 : shabbat_ru,
                'Shabbos'                : shabbat_en,
                'Рош Ходеш'              : rosh_chodesh_ru,
                'Rosh Chodesh'           : rosh_chodesh_en,
                'Праздники'              : holidays_ru,
                'Holidays'               : holidays_en,
                'Посты'                  : fasts_ru,
                'Fast days'              : fasts_en,
                'Даф Йоми'               : daf_ru,
                'Daf Yomi'               : daf_en,
                'Обновить местоположение': update_location_ru,
                'Update location'        : update_location_en,
                'Назад'                  : main_menu,
                'Back'                   : main_menu,
                'ЧаВо'                   : faq_ru,
                'F.A.Q.'                 : faq_en,
                '🇷🇺'                     : faq_ru,
                '🇱🇷'                     : faq_en,
                'Сообщить об ошибке'     : report_ru,
                'Contact'           : report_en,
                'Рош Ашана'              : rosh_hashana_ru,
                'Rosh HaShanah'          : rosh_hashana_en,
                'Йом Кипур'              : yom_kippur_ru,
                'Yom Kippur'             : yom_kippur_en,
                'Суккот'                 : succot_ru,
                'Succos'                 : succot_en,
                'Шмини Ацерет'           : shmini_atzeret_ru,
                'Shmini Atzeres'         : shmini_atzeret_en,
                'Ханука'                 : chanukah_ru,
                'Chanukah'               : chanukah_en,
                'Ту биШват'              : tu_beshvat_ru,
                'Tu BShevat'             : tu_beshvat_en,
                'Пурим'                  : purim_ru,
                'Purim'                  : purim_en,
                'Пейсах'                 : pesach_ru,
                'Pesach'                 : pesach_en,
                'Лаг баОмер'             : lag_baomer_ru,
                'Lag BaOmer'             : lag_baomer_en,
                'Шавуот'                 : shavuot_ru,
                'Shavuot'                : shavuot_en,
                '15 Ава'                 : tu_beav_ru,
                'Tu BAv'                 : tu_beav_en,
                'Израильские праздники'  : israel_ru,
                'Israel holidays'        : israel_en,
                'Пост Гедалии'           : fast_gedaliah_ru,
                'Tzom Gedaliah'          : fast_gedaliah_en,
                '10 Тевета'              : asarah_betevet_ru,
                'Asarah BTevet'          : asarah_betevet_en,
                'Пост Эстер'             : fast_esthet_ru,
                'Taanit Esther'          : fast_esther_en,
                '17 Таммуза'             : sheva_asar_betammuz_ru,
                'Shiva Asar BTammuz'     : sheva_asar_betammuz_en,
                '9 Ава'                  : tisha_beav_ru,
                'Tisha BAv'              : tisha_beav_en,
                }
    command_name = commands.get(command, incorrect_text)
    commando = command_name(user)
    if type(commando) == str:  # для обычных строк, отправляемых ботом
        bot.send_message(user, commando, parse_mode='Markdown')
    elif type(commando) == tuple:  # для строк с клавиатурой
        bot.send_message(user,
                         commando[0],
                         reply_markup=commando[1],
                         parse_mode='Markdown'
                         )
    elif type(commando) == list:  # для строк без пред. просмотра
        bot.send_message(user,
                         commando,
                         disable_web_page_preview=True
                         )

