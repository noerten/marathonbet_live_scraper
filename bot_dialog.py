import time
import logging
import sys
import telebot
from time import sleep

import config
from scrape_marathonbet_live_volleyball import load_pickle
from scrape_marathonbet_live_volleyball import save_pickle
from scrape_marathonbet_live_volleyball import get_total
from scrape_marathonbet_live_volleyball import get_link


bot = telebot.TeleBot(config.TG_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    reply = ('Возможные команды:\nчтобы установить новый тотал: /total,\n'
             'чтобы указать новую ссылку на страницу волейбола: /link,\n'
             'чтобы увидеть последнюю запись лога: /show_log')
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['total'])
def total(message):
    total = get_total()
    reply_text = ('Текущий тотал {}. Для установки нового тотала введите'
                  ' число'.format(total))
    reply = bot.send_message(message.chat.id, reply_text)
    bot.register_next_step_handler(reply, set_total)


def set_total(message):
    try:
        new_total = float(message.text)
        save_pickle(new_total, config.CUSTOM_TOTAL_PICKLE)
        total = get_total()
        bot.send_message(message.chat.id, 'Новый тотал {}'.format(total))
    except ValueError:
        message_text = ('Необходимо ввести число (разделитель точка, '
                   'например, 44.5). Начните сначала.')
        bot.send_message(message.chat.id, message_text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Начните сначала')


@bot.message_handler(commands=['link'])
def link(message):
    link = get_link()
    reply_text =  ('Текущая ссылка {}. Для установки новой ссылки вставьте '
                   'ссылку, она должна '
                   'начинаться с http'.format(link))
    reply = bot.send_message(message.chat.id, reply_text,
                             disable_web_page_preview=True)
    bot.register_next_step_handler(reply, set_link)


def set_link(message):
    try:
        new_link = message.text
        if new_link.startswith('http'):
            save_pickle(new_link, config.CUSTOM_LINK_PICKLE)
            link = get_link()
            bot.send_message(message.chat.id,
                             'Новая ссылка {}'.format(link),
                             disable_web_page_preview=True)
        else:
            message_text = ('Ссылка должна начинаться с http. Начните сначала.')
            bot.send_message(message.chat.id, message_text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Начните сначала')


@bot.message_handler(commands=['show_log'])
def show_log(message):
    log = get_last_line('bot_log.log').rstrip()
    reply_text = ('Если время в логе (МСК) примерно соответствует текущему, '
                  'все хорошо. Если нет, попробуйте перезапустить сервер и '
                  'запустить бота (`start_bot.sh`)\n{}'.format(log))
    reply = bot.send_message(message.chat.id, reply_text)


def get_last_line(filepath):
    with open(filepath, 'rb') as fh:
        last = fh.readlines()[-1].decode()
        return last


if __name__ == '__main__':
    bot.polling(none_stop=True)
    
