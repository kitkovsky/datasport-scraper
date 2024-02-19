import time
from typing import Literal

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver

LocatorStrategy = Literal[
    "id",
    "xpath",
    "link text",
    "partial link text",
    "name",
    "tag name",
    "class name",
    "css selector",
]


def find_and_click(
    driver: WebDriver,
    by: LocatorStrategy,
    value: str,
    action: Literal["click", "send_keys"] = "click",
    scroll: bool = False,
) -> None:
    element = driver.find_element(by, value)
    if scroll:
        element_height = int(element.rect.get("y") or 10)
        ActionChains(driver).scroll_by_amount(0, element_height // 2).perform()

    time.sleep(1)

    if action == "click":
        element.click()
    else:
        element.send_keys("\n")

    return
