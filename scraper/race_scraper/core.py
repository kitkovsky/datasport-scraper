import os
from contextlib import closing
from typing import Any, List

import libsql_experimental as libsql
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

RACES_SCRAPE_LIMIT = int(os.getenv("RACES_SCRAPE_LIMIT", 0))
DB_URL = os.getenv("DB_URL")
DB_AUTH_TOKEN = os.getenv("DB_AUTH_TOKEN")

conn = libsql.connect(database=DB_URL, auth_token=DB_AUTH_TOKEN)


def get_scrapable_races_list() -> List[Any]:
    datasport_req = requests.get(DATASPORT_RESULTS_URL)
    datasport_soup = BeautifulSoup(datasport_req.content, "html.parser")

    all_race_tags = datasport_soup.find_all("a")

    races_to_scrape = list(filter(should_scrape_race, all_race_tags))

    return (
        races_to_scrape[0:RACES_SCRAPE_LIMIT] if RACES_SCRAPE_LIMIT else races_to_scrape
    )


def scrape_race(race, driver: WebDriver) -> None:
    race_results_page_url = race["href"]
    print(f"scraping race: {race_results_page_url}")

    driver.get(race_results_page_url)

    race = get_race_info(driver)

    with closing(conn.cursor()) as cur:
        cur.execute(
            "INSERT INTO races (datasport_race_id, name, distance) VALUES (?, ?, ?);",  # noqa: E501
            (race["datasport_race_id"], race["name"], race["distance"]),
        )

        for participant in race["participants"]:
            cur.execute(
                "INSERT INTO participants (name, age, gender, finish_time, finished, started, disqualified, datasport_race_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",  # noqa: E501
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


def should_scrape_race(race_tag: Any) -> bool:
    # some of the races don't have the number of participants, hence the `or "0"`
    has_any_participants = int(race_tag.find("span").text or "0") > 0

    if not has_any_participants:
        return False

    # href format: https://wyniki.datasport.pl/results4570
    datasport_race_id = race_tag.get("href").split("results")[1]
    has_been_scraped = False

    with closing(conn.cursor()) as cur:
        cur.execute(
            "SELECT * FROM races WHERE datasport_race_id = ?;",
            (datasport_race_id,),
        )
        result = cur.fetchone()
        has_been_scraped = result is not None

    return not has_been_scraped
