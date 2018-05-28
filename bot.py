# -*- coding: utf-8 -*-
import logging
import cherrypy
import telebot
import botan
import config
import text_handler
import functions as f
from logging.handlers import RotatingFileHandler


WEBHOOK_HOST = '188.42.195.141'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу
WEBHOOK_URL_BASE = 'https://{}:{}'.format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = '/{}/'.format(config.TOKEN)


bot = telebot.TeleBot(config.TOKEN)


# сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers \
                and 'content-type' in cherrypy.request.headers \
                and cherrypy.request.headers['content-type'] == \
                'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=['start'])
def handle_start(message):
    f.check_id_in_db(message.from_user)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Русский', 'English')
    bot.send_message(message.from_user.id,
                     'Выберите язык/Choose the language',
                     reply_markup=user_markup
                     )
    logger.info(f' Command: \'\start\', from: {message.from_user.id}')
    botan.track(config.BOTAN_KEY, message.from_user.id, message, '/start')


@bot.message_handler(commands=['help'])
def handle_help(message):
    f.check_id_in_db(message.from_user)
    menu = telebot.types.ReplyKeyboardMarkup(True, False)
    menu.row('🇷🇺', '🇱🇷', 'Назад/Back')
    help_str = 'Пожалуйста, выберите язык справки'
    bot.send_message(message.from_user.id,
                     help_str,
                     reply_markup=menu)
    logger.info(f' Command: \'\help\', from: {message.from_user.id}')
    botan.track(config.BOTAN_KEY, message.from_user.id, message, '/help')


@bot.message_handler(commands=['report'])
def handle_report(message):
    f.check_id_in_db(message.from_user)
    report_str = 'Чтобы сообщить об ошибке, пожалуйста, напишите сюда: \n' \
                 't.me/benyomin, или сюда: \nt.me/Meir_Yartzev. \nПожалуйста,'\
                 ' убедитесь, что вы ознакомились с часто задаваемыми' \
                 ' вопросами, доступными по команде /help\n\nFor bug report ' \
                 'please write to \nt.me/benyomin or \nt.me/Meir_Yartzev. ' \
                 '\nPlease, make sure that you had been read '\
                 'F.A.Q. available by command /help'
    bot.send_message(message.from_user.id,
                     report_str,
                     disable_web_page_preview=True)
    logger.info(f' Command: \'\report\', from: {message.from_user.id}')
    botan.track(config.BOTAN_KEY, message.from_user.id, message, '/report')


@bot.message_handler(func=lambda message: True, content_types=['location',
                                                               'venue'])
def handle_text(message):
    f.check_id_in_db(message.from_user)
    if f.check_location(message.from_user.id,
                        message.location.latitude,
                        message.location.longitude,
                        bot
                        ):
        text_handler.make_response('Back', message.from_user.id, bot)
        tz = f.get_tz_by_location(f.get_location_by_id(message.from_user.id))
        f.check_tz(message.from_user.id, tz)
        logger.info(f' Location: '
                    f'{message.location.latitude}, '
                    f'{message.location.longitude}, '
                    f'from: {message.from_user.id}')
        botan.track(config.BOTAN_KEY, message.from_user.id, message, 'Получил геометку')


@bot.message_handler(regexp=r'^-?\d{1,2}\.{1}\d+, {0,1}-?\d{1,3}\.{1}\d+$')
def handle_text(message):
    f.check_id_in_db(message.from_user)
    loc = message.text.split(sep=', ')
    if loc[0] == message.text:
        loc = message.text.split(sep=',')
    if f.check_location(message.from_user.id, loc[0], loc[1], bot):
        text_handler.make_response('Back', message.from_user.id, bot)
        logger.info(f' Text location: {loc[0]}, {loc[1]}, '
                    f'from: {message.from_user.id}')
        tz = f.get_tz_by_location(f.get_location_by_id(message.from_user.id))
        f.check_tz(message.from_user.id, tz)
        botan.track(config.BOTAN_KEY,
                    message.from_user.id,
                    message,
                    'Получил текстовую геометку'
                    )



@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    f.check_id_in_db(message.from_user)
    text_handler.make_response(message.text, message.from_user.id, bot)
    logger.info(f' Text: {message.text}, from: {message.from_user.id}')
    botan.track(config.BOTAN_KEY, message.from_user.id, message, message.text)


cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})


if __name__ == '__main__':
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('logs/bot_logger',
                                  maxBytes=1024*1024*3,
                                  backupCount=20)
    formatter = logging.Formatter(fmt='%(filename)s[LINE:%(lineno)d]# ' \
                                      '%(levelname)-8s [%(asctime)s]  '
                                      '%(message)s'
                                  )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
    
  
