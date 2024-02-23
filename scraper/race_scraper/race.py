from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


def get_race_distance(driver: WebDriver) -> float | None:
    distance = None

    # some indoor races don't have a distance
    try:
        # tag format: "15.0 km"
        last_checkpoint_tag = driver.find_element(By.ID, "profildiv").find_elements(
            By.TAG_NAME, "a"
        )[-1]
        distance = float(last_checkpoint_tag.text.split(" ")[0])
    except IndexError:
        pass

    return distance


def get_race_title(driver: WebDriver) -> str:
    #                             - always 5 spaces -
    # tag format: "41. Bieg Chomiczówki     2024-02-11 Warszawa"
    title_tag = driver.find_element(By.ID, "zawodytytul").text
    return title_tag.split("     ")[0]


def get_race_datasport_id(driver: WebDriver) -> int:
    # url format: "https://wyniki.datasport.pl/results4714/indexnew.php"
    current_url = driver.current_url
    return int(current_url.split("/")[-2].replace("results", ""))
