import os
from typing import Any, List

import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.chrome.webdriver import WebDriver

from race_scraper.participant import get_race_participants
from race_scraper.race import (
    Race,
    get_race_datasport_id,
    get_race_distance,
    get_race_title,
)

load_dotenv()

DATASPORT_RESULTS_URL = "https://wyniki.datasport.pl"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
)


def get_scrapable_races_list() -> List[Any]:
    datasport_req = requests.get(DATASPORT_RESULTS_URL)
    datasport_soup = BeautifulSoup(datasport_req.content, "html.parser")

    all_race_tags = datasport_soup.find_all("a")

    races_with_participants = list(
        # some of the races don't have the number of participants, hence the `or "0"`
        filter(lambda race: int(race.find("span").text or "0") > 0, all_race_tags)
    )

    # TODO: this should also check if the race.datasport_race_id has already been scraped  # noqa: E501
    # if not, add it to the list
    # but the first scrape should be run without this, just scrape everything

    return races_with_participants


def scrape_race(race, driver) -> None:
    race_results_page_url = race["href"]
    print(f"scraping race: {race_results_page_url}")

    driver.get(race_results_page_url)

    race = get_race_info(driver)

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO races (datasport_race_id, name, distance) VALUES (%s, %s, %s);",  # noqa: E501
            (race["datasport_race_id"], race["name"], race["distance"]),
        )

        for participant in race["participants"]:
            cur.execute(
                "INSERT INTO participants (name, age, gender, finish_time, finished, started, disqualified, datasport_race_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",  # noqa: E501
                (
                    participant["name"],
                    participant["age"],
                    participant["gender"],
                    participant["finish_time"],
                    participant["finished"],
                    participant["started"],
                    participant["disqaualified"],
                    race["datasport_race_id"],
                ),
            )
    conn.commit()


def get_race_info(driver: WebDriver) -> Race:
    datasport_race_id = get_race_datasport_id(driver)
    title = get_race_title(driver)
    distance = get_race_distance(driver)
    participants = get_race_participants(driver)

    return {
        "datasport_race_id": datasport_race_id,
        "name": title,
        "distance": distance,
        "participants": participants,
    }
