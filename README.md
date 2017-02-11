# scrape_marathonbet_live_voleyball

Script scrapes marathonbet live volleyball [page](https://www.marathonbet.com/su/?sportLive=23690), looks for matches with total for each of first two sets more than some predefined number and sends it to email. Also here telegram bot that can send updates to telegram channel and  using bot one can change threshold total and link scraper works with.


## Installation

Just copy the files and create `private_config.py` and define `TG_TOKEN`, `TG_CHANNEL_NAME` in it.

## Usage

Either run from console `python scrape_marathonbet_live_voleyball.py` (you will need to create `email_config.py` with variables (their names are the same as in config.py) containg sender's email, recepient's email and sender's password) and get a single update to email or run both 'bot_channel.py' and 'bot_dialog.py' in order to get updates to telegram channel and be able to change values using bot.
