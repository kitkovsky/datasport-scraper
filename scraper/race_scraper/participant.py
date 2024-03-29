import datetime
import sys
from typing import List, Literal, TypedDict

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

sys.path.append("..")

from db.models import Participant
from race_scraper.utils import find_and_click

TimeTag = TypedDict(
    "TimeTag",
    {
        "milliseconds": int | None,
        "finished": bool,
        "started": bool,
        "disqualified": bool,
    },
)


def get_race_participants(
    driver: WebDriver, datasport_race_id: int
) -> List[Participant]:
    participants: List[Participant] = []

    print("searching for results_accordion")
    # results accordion
    find_and_click(driver, By.ID, "a1but1")

    print("searching for open_leader_board_accordion")
    # open category leader board accordion
    find_and_click(driver, By.XPATH, "//small[text()='Open']", scroll=True)

    try:
        print("searching for show_all_rows_button")
        # show all rows button
        find_and_click(
            driver,
            By.XPATH,
            "//button[contains(text(), 'Pokaż wszystkich / Show all')]",
            "send_keys",
        )
    except NoSuchElementException:
        # some races don't have enough participants to have this button
        pass

    print("searching for all_rows")
    all_rows = driver.find_element(By.ID, "bodyopen1").find_elements(By.TAG_NAME, "tr")

    print("filtering rows")
    # [0::2] because every participant has two rows assigned to them, but we only need the first one  # noqa: E501
    filtered_rows = list(filter(lambda row: not is_special_row(row), all_rows))[0::2]

    print("extracting participants info")
    for row in filtered_rows:
        participant = get_participant_info(row, datasport_race_id)
        participants.append(participant)

    return participants


def is_special_row(row: WebElement) -> bool:
    is_crown_row = row.get_attribute("style") == "border-bottom: thick double grey;"

    is_overwritten_time_row = (
        row.find_elements(
            By.XPATH,
            ".//td/i[@class='me-1 bi bi-exclamation-diamond']",
        )
        != []
    )

    return is_overwritten_time_row or is_crown_row


def get_participant_info(row: WebElement, datasport_race_id: int) -> Participant:
    # tag format:
    #   """
    #   JAN KOWALSKI (1017)
    #   WARSZAWA ur.1995
    #   """
    name_and_age_tag = row.find_element(
        By.XPATH, ".//a[@style='text-decoration:none;']"
    ).text
    name = name_and_age_tag[: name_and_age_tag.index("(") - 1].title()
    birth_year = int(name_and_age_tag.split("ur.")[1].strip())
    age = datetime.datetime.now().year - birth_year

    category_tag = row.find_elements(By.TAG_NAME, "td")[6].text

    def gender(tag: str) -> Literal["M", "F"] | None:
        if "M" in tag:
            return "M"
        if "K" in tag:
            return "F"
        return None

    finish_time_tag = row.find_elements(By.TAG_NAME, "td")[5].text
    time_tag = convert_time_tag(finish_time_tag)

    return Participant(
        name=name,
        age=age,
        gender=gender(category_tag),
        finish_time=time_tag["milliseconds"],
        finished=time_tag["finished"],
        started=time_tag["started"],
        disqualified=time_tag["disqualified"],
        datasport_race_id=datasport_race_id,
    )


def convert_time_tag(time_tag: str) -> TimeTag:
    """
    Args:
        time_tag (str): example: "1:02:00", "25:00", "DNS", "DNF"

    Example:
        convert_time_tag("1:02:00") -> 3_720_000
        convert_time_tag("25:00") -> 1_500_000
        convert_time_tag("02:19,47") -> 139_470
    """
    if time_tag in ["DNS", "(0.00 km)"]:
        return TimeTag(
            milliseconds=None, finished=False, started=False, disqualified=False
        )
    # participants can sometimes have a time tag for running only a part of the race,
    # in this case the tag inlcudes the distance ran in parentheses, like "(8.00 km)"
    if time_tag == "DNF" or any(char in ["(", ")"] for char in time_tag):
        return TimeTag(
            milliseconds=None, finished=False, started=True, disqualified=False
        )
    if time_tag == "DSQ":
        return TimeTag(
            milliseconds=None, finished=False, started=True, disqualified=True
        )

    # input format:
    # """
    # 46:14 3.04/km
    # +00:00
    # or with miliseconds
    # 02:19,47 1.46/km
    # +00:00
    # """
    total_milliseconds = 0

    time_tag = time_tag.split(" ")[0]
    has_milliseconds = "," in time_tag

    if has_milliseconds:
        milliseconds_part = int(time_tag.split(",")[1]) * 10
        total_milliseconds += milliseconds_part
        time_tag = time_tag.split(",")[0]

    time_tag_parts = time_tag.strip().split(":")
    time_tag_parts.reverse()

    for idx, part in enumerate(time_tag_parts):
        total_milliseconds += int(part) * (60**idx) * 1000

    return TimeTag(
        milliseconds=total_milliseconds,
        finished=True,
        started=True,
        disqualified=False,
    )
