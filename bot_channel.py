import logging
import random
import time

import telebot

import config
from scrape_marathonbet_live_volleyball import marathon


bot = telebot.TeleBot(config.TG_TOKEN)


def send_update(text):
    bot.send_message(config.TG_CHANNEL_NAME, text,
                     disable_web_page_preview=True)


def run_bot():
    logging.info('[BOT] started scanning')
    result = marathon()
    if result:
        matches_info = result[1]
        logging.info('[BOT] got info from marathon module')
        send_update(matches_info)
        logging.info('[BOT] sent update')
    else:
        logging.info('[BOT] nothing changed')


if __name__ == '__main__':
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logger_format = ('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s '
                     '- %(message)s')
    logging.basicConfig(format=logger_format, level=logging.INFO,
                        filename=config.LOG_NAME, datefmt='%d.%m.%Y %H:%M:%S')
    if not config.SINGLE_RUN:
        while True:
            run_bot()
            print(time.strftime("%a, %d %b %Y %X", time.localtime()))
            logging.info('[BOT] Script went to sleep.')
            time.sleep(random.uniform(15, 25))
    else:
        run_bot()
    logging.info('[BOT] Script exited.\n')
