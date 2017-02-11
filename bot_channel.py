import time
import logging
import random
import sys
import telebot
from time import sleep

import config
from scrape_marathonbet_live_volleyball import marathon


bot = telebot.TeleBot(config.TG_TOKEN)

def send_update(text):
    bot.send_message(config.TG_CHANNEL_NAME, text, disable_web_page_preview=True)
    # parse_mode='HTML',

def run_bot():
    logging.info('[BOT] started scanning')
    result = marathon()
    if result:
        info = result[1]
        logging.info('[BOT] got info from marathon module')
        send_update(info)
        logging.info('[BOT] sent update')
    else:
        logging.info('[BOT] nothing changed')


if __name__ == '__main__':
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        filename='bot_log.log', datefmt='%d.%m.%Y %H:%M:%S')
    if not config.SINGLE_RUN:
        mistake_counter = 0
        while mistake_counter < 30:
            try:
                run_bot()
                mistake_counter = 0
            except Exception:
                mistake_counter += 1
                logging.error('[BOT] mistake_counter {}'.format(mistake_counter))
                logging.error(traceback.format_exc())

            print(time.strftime("%a, %d %b %Y %X", time.localtime()))
            logging.info('[BOT] Script went to sleep.')
            time.sleep(random.uniform(15,25))
        send_update('Случилось 30 ошибок подряд, что-то не так, '
                    'бот отключился')
    else:
        counter = 0
        while counter < 10:
            try:
                run_bot()
                break
            except:
                counter += 1
                logging.error('[BOT] mistake_counter {}'.format(counter))
                logging.error(traceback.format_exc())
                time.sleep(random.uniform(15,25))
        if counter == 10:
            send_update('Случилось 10 ошибок подряд, что-то не так, '
                        'бот отключился')

    logging.info('[BOT] Script exited.\n')
