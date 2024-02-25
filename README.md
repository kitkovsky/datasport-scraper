# Datasport Scraper
A Selenium and Beautiful Soup based web scraper for scraping race results from [wyniki.datasport.pl](https://wyniki.datasport.pl).\
Currently able to save (per race):
- race (datasport id, name, distance)
- list of participants (name, age, gender, finish time, has finished, has started, is disqualified)

***

App URL: [imperial-ally-414513-ej4pzz4pbq-lm.a.run.app](https://imperial-ally-414513-ej4pzz4pbq-lm.a.run.app)\
Available API routes:
- `/races` - all races
- `/races/{datasport_race_id}` - race details


## How to get going

### Developing
Create a virtual environment in the root of the project. Each app has its own requirements file:
- `requirements.txt` - shared between all apps
- `scraper/requirements.txt`
- `backend/requirements.txt`
- `db/requirements.txt`

### Backend
1. `docker-compose up` starts a local Flask app that reads from a `db/sqlite.db` file

### Scraper
Execute all commands from `scraper` directory with the root virtual env sourced.

1. Grab your chromedriver from [here](https://googlechromelabs.github.io/chrome-for-testing) and place it in the `scraper` directory
3. `chmod +x scrape`
3. `./scrape` will run the scraper and save results to the db

`RACES_SCRAPE_LIMIT` variable in `scraper/.env` will set the limit of scraped races per run. When set to nothing, the scraper will scrape all available races.
