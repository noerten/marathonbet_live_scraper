try:
    import email_config
except ImportError:
    email_config = None
    logging.warning('no email config')

import private_config


if email_config:
    MSG_FROM = email_config.MSG_FROM
    PASSWORD = email_config.PASSWORD
    MSG_TO = email_config.MSG_TO
else:
    MSG_FROM = None
    PASSWORD = None
    MSG_TO = None

TG_TOKEN = private_config.TG_TOKEN
TG_CHANNEL_NAME = private_config.TG_CHANNEL_NAME

SINGLE_RUN = False
DEFAULT_LINK = 'https://www.marathonbet.com/su/live/23690'
DEFAULT_TOTAL = 45.5
CUSTOM_LINK_PICKLE = 'custom_link.pickle'
CUSTOM_TOTAL_PICKLE = 'custom_total.pickle'
MATCH_TIMESTAMP_PICKLE = 'match_timestamp.pickle'
LOG_NAME = 'bot_log.log'
