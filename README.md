# marathonbet_live_scraper

Script scrapes marathonbet live volleyball [page](https://www.marathonbet.com/su/?sportLive=23690), looks for matches with total for each of first two sets more than some predefined number and sends it to email. Also here telegram bot that can send updates to telegram channel and  using bot one can change threshold total and link scraper works with.


## Installation

Install requirements `pip3 install requirements.txt`, create `private_config.py` and define `TG_TOKEN`, `TG_CHANNEL_NAME` in it. If you want to send emails, create `email_config.py` and define `MSG_FROM`, `PASSWORD`, `MSG_TO`. Also see [here]() installation to VPS guide (in Russian).

## Usage

Either run from console `python3 scrape_marathonbet_live_volleyball.py` (you will need `email_config.py`) and get a single update to email or run both 'bot_channel.py' and 'bot_dialog.py' in order to get updates to telegram channel and to be able to change values using bot.