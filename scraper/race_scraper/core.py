import os
import sys
from typing import Any, List, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.chrome.webdriver import WebDriver

from race_scraper.participant import get_race_participants
from race_scraper.race import (
    get_race_datasport_id,
    get_race_distance,
    get_race_title,
)

sys.path.append("..")

from db.connection import session
from db.models import Participant, Race

load_dotenv()

DATASPORT_RESULTS_URL = "https://wyniki.datasport.pl"

RACES_SCRAPE_LIMIT = int(os.getenv("RACES_SCRAPE_LIMIT", -1))


def get_scrapable_races_list() -> List[Any]:
    datasport_req = requests.get(DATASPORT_RESULTS_URL)
    datasport_soup = BeautifulSoup(datasport_req.content, "html.parser")

    all_race_tags = datasport_soup.find_all("a")

    races_to_scrape = []

    for race_tag in all_race_tags:
        if should_scrape_race(race_tag):
            races_to_scrape.append(race_tag)
        if len(races_to_scrape) == RACES_SCRAPE_LIMIT:
            break

    return races_to_scrape


def scrape_race(race, driver: WebDriver) -> None:
    race_results_page_url = race["href"]
    print(f"scraping race: {race_results_page_url}")

    driver.get(race_results_page_url)

    race, participants = get_race_info(driver)

    session.add(race)
    session.add_all(participants)

    session.commit()


def get_race_info(driver: WebDriver) -> Tuple[Race, List[Participant]]:
    datasport_race_id = get_race_datasport_id(driver)
    title = get_race_title(driver)
    distance = get_race_distance(driver)
    participants = get_race_participants(driver, datasport_race_id)

    return Race(
        datasport_race_id=datasport_race_id, name=title, distance=distance
    ), participants


def should_scrape_race(race_tag: Any) -> bool:
    # some of the races don't have the number of participants, hence the `or "0"`
    has_any_participants = int(race_tag.find("span").text or "0") > 0

    if not has_any_participants:
        return False

    # href format: https://wyniki.datasport.pl/results4570
    datasport_race_id = race_tag.get("href").split("results")[1]
    has_been_scraped = False

    if session.query(Race).where(Race.datasport_race_id == datasport_race_id).first():
        has_been_scraped = True

    return not has_been_scraped
