from os import system
from json import load
from time import sleep
from mail import send_email
from selenium import webdriver
from random import choice, shuffle
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from logger import logging, config, LOG_CONFIG
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import \
    WebDriverException, SessionNotCreatedException, TimeoutException

PROXY_FILE = "./proxies.json"

RESOLUTIONS = ["1920,1080", "1600,900", "1366,768", "1280,800", 
               "1280,720", "1024,768", "800,600", "640,480", "320,240"]

AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4389.82 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4430.85 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4430.85 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4430.85 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4430.85 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4430.85 Safari/537.36"]

PAGE_LOAD_TIMEOUT = 60
PAGE_DOWNLOAD_TIMEOUT = 60
PROXIES_TIMEOUT_LIMIT = 35

URL = "https://www.hermes.com/nl/en/category/women/bags-and-small-leather-goods/bags-and-clutches/#|"

config(LOG_CONFIG)

logging.debug("Running the bot with the following global settings:")
logging.debug(f"PAGE_LOAD_TIMEOUT = {PAGE_LOAD_TIMEOUT}")
logging.debug(f"PAGE_DOWNLOAD_TIMEOUT = {PAGE_DOWNLOAD_TIMEOUT}")
logging.debug(f"PROXIES_TIMEOUT_LIMIT = {PROXIES_TIMEOUT_LIMIT}")
logging.debug(f"TARGET URL = {URL}")
logging.debug(f"LOGGING CONFIGURATION = {LOG_CONFIG}")


def run_spiders():
    system("scrapy crawl arachne -O proxies.json")
    sleep(10)

def fetch_proxies():
    with open(PROXY_FILE) as f:
        proxies = load(f)
        shuffle(proxies)
        for proxy in proxies:
            yield proxy["IP Address"], proxy["Port"]


def create_driver(ip, port):
    window_size = choice(RESOLUTIONS).split(',')
    firefox_options = webdriver.FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", ip)
    profile.set_preference("network.proxy.http_port", int(port))
    profile.set_preference("network.proxy.ssl", ip)
    profile.set_preference("network.proxy.ssl_port", int(port))
    profile.set_preference("general.useragent.override", choice(AGENTS))
    profile.set_preference("browser.download.folderList", 2)
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--enable-javascript")
    driver = webdriver.Firefox(
        firefox_options=firefox_options,
        firefox_profile=profile
    )
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.set_window_size(int(window_size[0]), int(window_size[1]))
    return driver

def validate_html(html):
    body = HtmlResponse(url=URL, body=html, encoding='utf-8')
    try: assert not "captcha" in body.css('script[src]::attr(src)').get()
    except TypeError: pass

def parse_html(html):
    body = HtmlResponse(url=URL, body=html, encoding='utf-8')
    products = []
    for tag in body.css("span.product-item-name"):
        products.append(tag.css("::text").get())
    return set(products)

def main(rest=60):
    logging.info("Acquiring the proxies list.")
    proxy = fetch_proxies()
    logging.info("Control loop started.")
    timeout_count = 0
    results = set()
    while True:
        try: ip, port = next(proxy)
        except StopIteration:
            logging.error("Consumed all existing proxies, acquiring new.")
            timeout_count = 0
            run_spiders()
        if timeout_count > PROXIES_TIMEOUT_LIMIT:
            logging.error("Too many timeouts occurred, updating the proxies.")
            timeout_count = 0
            run_spiders()
        logging.info(f"Instantiating a driver with proxy: {ip}:{port}.")
        driver = create_driver(ip, port)
        try:
            logging.info(f"Attempting to get the page.")
            driver.get(URL)
            wait = WebDriverWait(driver, PAGE_DOWNLOAD_TIMEOUT)
            logging.info(f"Validating the page.")
            validate_html(driver.page_source)
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "product-item-name")))
            logging.info("Parsing the page.")
            new_results = parse_html(driver.page_source)
            if (results != new_results  and
                results != set()):
                new_items = new_results-results
                if new_items != set():
                    logging.warn(f"New items {new_items} has been found!")
                    send_email(f"The following products has been added \
                               to the Hermes store: {new_items}")
            results = new_results
            logging.info(f"Data acquired: {results}.")
            logging.info(f"Going to seelp for {rest}s")
            driver.quit()
            sleep(rest)
            continue
        except (WebDriverException, AssertionError,
                SessionNotCreatedException) as error:
            if type(error) == AssertionError:
                logging.error(
                    "The site has blocked or detected us as bot, moving on to the next proxy.")
            elif (type(error) == WebDriverException or
                 type(error) == SessionNotCreatedException or
                 type(error) == TimeoutException):
                timeout_count += 1
                logging.error(
                    "The proxy has timed-out, moving on to the next proxy.")
            driver.quit()
            continue

if __name__ == "__main__":
    main()
