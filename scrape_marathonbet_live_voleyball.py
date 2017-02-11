import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import smtplib
import sys
import time

import requests
from bs4 import BeautifulSoup

import config


VOLLEYBALL_LINK = 'https://www.marathonbet.com/su/?sportLive=23690'
TOTAL = 45.5


def make_soup(html):
    return BeautifulSoup(html, 'html.parser')


def get_html(url):
    return requests.get(url).text


def get_all_matches_info(html):
    soup = make_soup(html)
    cont = soup.find('div', id='liveCategoriesContainer')
    all_matches_info = []
    for tournament_cont in cont.find_all('div', class_='category-container'):
        tournament_soup = tournament_cont.find('table', class_='foot-market')
        for match_soup in tournament_soup.find_all('tbody', recursive=False):
            names = match_soup.find_all('div',
                                        class_='live-today-member-name')
            teams = [names[0].get_text(), names[1].get_text()]
            teams = ' vs '.join(teams)
            current = match_soup.find('div',
                                      class_='cl-left red').get_text().strip()
            
            match_info = [teams, current]
            all_matches_info.append(match_info)
    return all_matches_info


def check_if_total_more(match_info):
    set_list = match_info[1].split(' ',1)[1].strip('()').split(', ')
    if len(set_list) > 1:
        good_sets = 0
        two_sets = [a_set.strip().split(':') for a_set in set_list[:2]]
        for a_set in two_sets:
            a_set_total = sum([int(game) for game in a_set])

            if a_set_total < TOTAL:
                break
            else:
                good_sets += 1
        return bool(good_sets == 2)


def send_simple_message(email_subject, email_text, msg_from=config.MSG_FROM,
                        msg_to=config.MSG_TO, password = config.PASSWORD):
    # in order to send from gmail acc you should turn on
    # 'less secured apps support' here
    # https://myaccount.google.com/security

    msg = MIMEMultipart('utf-8')
    msg['Subject'] = email_subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    msg.attach(MIMEText(email_text, 'plain'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(config.MSG_FROM, config.PASSWORD)
        server.sendmail(msg_from, [msg_to], msg.as_string())


def format_email_subject():
    sent_at = time.strftime("%a, %d %b %Y %X", time.localtime())
    return "Воллейбол, матчи с тоталом > {}, отправлено {}".format(TOTAL,
                                                                   sent_at)


def format_email_text(matches_to_send):
    title_str = ('Матчи с тоталом каждого из'
                 ' первых двух сетов больше {}\n'.format(TOTAL))

    matches_str = "\n\n".join("\n".join(l) for l in matches_to_send)
    return '\n'.join([title_str, VOLLEYBALL_LINK, matches_str]) 
    

def main():
    all_matches_info = get_all_matches_info(get_html(VOLLEYBALL_LINK))
    matches_to_send = []
    for match_info in all_matches_info:
        if check_if_total_more(match_info):
            matches_to_send.append(match_info)
    print(matches_to_send)
    email_text = format_email_text(matches_to_send)
    email_subject = format_email_subject()
    return email_subject, email_text
            


if __name__ == '__main__':
    start_time = time.time()
    counter = 0
    while counter < 10:
        try:
            email_text, email_subject = main()
            send_simple_message(email_text, email_subject)
            print('message sent')
            break
        except Exception as e:
            print(e)
            counter += 1
            time.sleep(random.uniform(5,15))
    print('it took', time.time() - start_time)
