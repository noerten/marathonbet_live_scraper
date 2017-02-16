from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import pickle
import random
import smtplib
import time
import traceback

import requests
from bs4 import BeautifulSoup

import config


def load_pickle(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def save_pickle(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def get_total():
    loaded_total = load_pickle(config.CUSTOM_TOTAL_PICKLE)
    total = loaded_total if loaded_total is not None else config.DEFAULT_TOTAL
    return total


def get_link():
    loaded_link = load_pickle(config.CUSTOM_LINK_PICKLE)
    link = loaded_link if loaded_link is not None else config.DEFAULT_LINK
    return link


def get_match_timestamp():
    loaded_dict = load_pickle(config.MATCH_TIMESTAMP_PICKLE)
    match_timestamp = loaded_dict if loaded_dict is not None else {}
    return match_timestamp


def make_soup(html):
    return BeautifulSoup(html, 'html.parser')


def get_html(url):
    return requests.get(url).text


def check_if_total_more(match_info, total):
    set_list = match_info[1].split(' ', 1)[1].strip('()').split(', ')
    if len(set_list) > 1:
        good_sets = 0
        two_sets = [a_set.strip().split(':') for a_set in set_list[:2]]
        for a_set in two_sets:
            a_set_total = sum([int(game) for game in a_set])

            if a_set_total < total:
                break
            else:
                good_sets += 1
        return bool(good_sets == 2)


def send_simple_message(email_subject, email_text, msg_from=config.MSG_FROM,
                        msg_to=config.MSG_TO, password=config.PASSWORD,
                        smtp_server="smtp.gmail.com", smtp_port=587):
    """in order to send from gmail acc you should turn on
    'less secured apps support' here
    https://myaccount.google.com/security
    """
    msg = MIMEMultipart('utf-8')
    msg['Subject'] = email_subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    msg.attach(MIMEText(email_text, 'plain'))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(config.MSG_FROM, password)
        server.sendmail(msg_from, [msg_to], msg.as_string())


def format_email_subject(total):
    sent_at = time.strftime("%a, %d %b %Y %X", time.localtime())
    return "Воллейбол, матчи с тоталом > {}, отправлено {}".format(total,
                                                                   sent_at)


def format_email_text(matches_to_send, total, link):
    title_str = ('Матчи с тоталом каждого из'
                 ' первых двух сетов больше {}\n'.format(total))
    matches_str = "\n\n".join("\n".join(l) for l in matches_to_send)
    return '\n'.join([title_str, link, matches_str]) 


def get_all_matches_info(html):
    soup = make_soup(html)
    if soup.find('a', class_='sport-category-label').get_text() != 'Волейбол':
        return [['error', 'неверная ссылка']]
    cont = soup.find('div', id='liveCategoriesContainer')
    if cont is None:
        cont = soup.find('div', id='container_EVENTS')
        if cont is None:
            return [['error', 'no container id=container_EVENTS']]
    all_matches_info = []
    tournament_conts = cont.find_all('div', class_='category-container')
    if tournament_conts is None:
        return [['error', 'no containers class_=category-container']]
    for tournament_cont in tournament_conts:
        tournament_soup = tournament_cont.find('table', class_='foot-market')
        if tournament_soup is None:
            return [['error', 'tournament_soup table, class=foot-market']] 
        match_soups = tournament_soup.find_all('tbody', recursive=False)
        if match_soups is None:
            return [['error', 'no match_soups tag=tbody']]      
        for match_soup in match_soups:
            names = match_soup.find_all('div',
                                        class_='live-today-member-name')
            if len(names) == 0:
                names = match_soup.find_all('div',
                                            class_='live-member-name')
                if len(names) == 0:
                    return [['error',
                             'no match names class=live-[today-]member-name']]
                    logging.error('class of names of commands has changed')
            teams = [names[0].get_text(), names[1].get_text()]
            teams = ' vs '.join(teams)
            current = match_soup.find('div',
                                      class_='cl-left red').get_text().strip()
            match_info = [teams, current]
            all_matches_info.append(match_info)
    return all_matches_info


def update_match_timestamp_pickle(match_timestamp_dict, time_to_live=6*60*60):
    for item in list(match_timestamp_dict):
        if time.time() - match_timestamp_dict[item] > time_to_live:
            match_timestamp_dict.pop(item)
    save_pickle(match_timestamp_dict, config.MATCH_TIMESTAMP_PICKLE)


def marathon():
    link = get_link()
    total = get_total()
    match_timestamp_dict = get_match_timestamp()
    counter = 0
    while counter < 10:
        all_matches_info = get_all_matches_info(get_html(link))
        if all_matches_info[0][0] != 'error':
            break
        else:
            counter += 1
            logging.info('trying to get all match info again '
                         'counter = {}'.format(counter))
            time.sleep(3)
    if all_matches_info[0][0] == 'error':
        error_tuple = (all_matches_info[0][0], all_matches_info[0][1],)
        if error_tuple in match_timestamp_dict:
            update_match_timestamp_pickle(match_timestamp_dict)
            return None
        else:
            match_timestamp_dict[error_tuple] = time.time()
            update_match_timestamp_pickle(match_timestamp_dict)
            return all_matches_info[0]
    matches_to_send = []
    for match_info in all_matches_info:
        match_title = match_info[0]
        if match_title in match_timestamp_dict:
            continue
        elif check_if_total_more(match_info, total):
            matches_to_send.append(match_info)
            match_timestamp_dict[match_info[0]] = time.time()
    update_match_timestamp_pickle(match_timestamp_dict)
    if len(matches_to_send) > 0:
        email_text = format_email_text(matches_to_send, total, link)
        email_subject = format_email_subject(total)
        return email_subject, email_text


if __name__ == '__main__':
    start_time = time.time()
    counter = 0
    while counter < 10:
        try:
            result = marathon()
            if result:
                email_text, email_subject = result
                send_simple_message(email_text, email_subject)
                print('message sent')
            break
        except:
            logging.error(traceback.format_exc())
            counter += 1
            time.sleep(random.uniform(5,15))
    print('it took', time.time() - start_time)
