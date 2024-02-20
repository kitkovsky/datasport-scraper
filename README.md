# Datasport Scraper
A Selenium and Beautiful Soup based web scraper for scraping race results from [wyniki.datasport.pl](https://wyniki.datasport.pl).\
Currently able to save (per race):
- race (datasport id, name, distance)
- list of participants (name, age, gender, finish time, has finished, has started, is disqualified)

***

Available API routes:
- `/races` - all races
- `/races/{datasport_race_id}` - race details


## How to get going

### Backend
1. `docker-compose up` starts a local postgres db and a Flask app

### Scraper
Execute all commands from `/scraper` directory.

1. Grab your chromedriver from [here](https://googlechromelabs.github.io/chrome-for-testing) and place it in the `/scraper` directory
2. `pip install -r requirements.txt`
3. `python main.py` will run the scraper and save results to the db

`RACES_SCRAPE_LIMIT` variable in `/scraper/.env` will set the limit of scraped races per run. When set to nothing, the scraper will scrape all available races.
