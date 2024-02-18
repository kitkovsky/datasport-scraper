import time
from typing import Literal

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
) -> None:
    element = driver.find_element(by, value)
    time.sleep(1)

    if action == "click":
        element.click()
    else:
        element.send_keys("\n")

    return
