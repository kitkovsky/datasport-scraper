import datetime
from typing import List, Literal, TypedDict

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from race_scraper.utils import find_and_click

Participant = TypedDict(
    "Participant",
    {
        "name": str,
        "age": int,
        "gender": Literal["M", "F"] | None,
        "finish_time": int | None,
        "finished": bool,
        "started": bool,
        "disqaualified": bool,
    },
)

TimeTag = TypedDict(
    "TimeTag",
    {"seconds": int | None, "finished": bool, "started": bool, "disqaualified": bool},
)


def get_race_participants(driver: WebDriver) -> List[Participant]:
    participants: List[Participant] = []

    print("searching for results_accordion")
    # results accordion
    find_and_click(driver, By.ID, "a1but1")

    print("searching for open_leader_board_accordion")
    # open category leader board accordion
    find_and_click(driver, By.XPATH, "//small[text()='Open']")

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

    for row in filtered_rows:
        participant = get_participant_info(row)
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


def get_participant_info(row: WebElement) -> Participant:
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

    return {
        "name": name,
        "age": age,
        "gender": gender(category_tag),
        "finish_time": time_tag["seconds"],
        "finished": time_tag["finished"],
        "started": time_tag["started"],
        "disqaualified": time_tag["disqaualified"],
    }


def convert_time_tag(time_tag: str) -> TimeTag:
    """
    Args:
        time_tag (str): example: "1:02:00", "25:00", "DNS", "DNF"

    Example:
        convert_time_tag_to_seconds("1:02:00") -> 3720
        convert_time_tag_to_seconds("25:00") -> 1500
    """
    if time_tag in ["DNS", "(0.00 km)"]:
        return TimeTag(seconds=None, finished=False, started=False, disqaualified=False)
    # participants can sometimes have a time tag for running only a part of the race,
    # in this case the tag inlcudes the distance ran in parentheses, like "(8.00 km)"
    if time_tag == "DNF" or any(char in ["(", ")"] for char in time_tag):
        return TimeTag(seconds=None, finished=False, started=True, disqaualified=False)
    if time_tag == "DSQ":
        return TimeTag(seconds=None, finished=False, started=True, disqaualified=True)

    # input format:
    # """
    # 46:14 3.04/km
    # +00:00
    # """
    total_seconds = 0

    time_tag = time_tag.split(" ")[0]
    time_tag_parts = time_tag.strip().split(":")
    time_tag_parts.reverse()

    for idx, part in enumerate(time_tag_parts):
        total_seconds += int(part) * (60**idx)

    return TimeTag(
        seconds=total_seconds, finished=True, started=True, disqaualified=False
    )
