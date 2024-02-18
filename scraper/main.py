from race_scraper.core import get_scrapable_races_list, scrape_race
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def main() -> None:
    races_to_scrape = get_scrapable_races_list()

    service = Service(executable_path="./chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)

    for race in races_to_scrape[0:1]:
        scrape_race(race, driver)

    driver.quit()


if __name__ == "__main__":
    main()
