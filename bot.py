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

# multiple resolutions & agents to be randomly chosen from to prevent fingerprinting
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

# configuration parameters for the run
PAGE_LOAD_TIMEOUT = 60
PAGE_DOWNLOAD_TIMEOUT = 60
PROXIES_TIMEOUT_LIMIT = 35

# target URL
URL = "https://www.hermes.com/nl/en/category/women/bags-and-small-leather-goods/bags-and-clutches/#|"

PROXY = "69.30.227.194"

# configuring the logger from the LOG_CONFIG dictionary found in logger.py
config(LOG_CONFIG)

logging.debug("Running the bot with the following global settings:")
logging.debug(f"PAGE_LOAD_TIMEOUT = {PAGE_LOAD_TIMEOUT}")
logging.debug(f"PAGE_DOWNLOAD_TIMEOUT = {PAGE_DOWNLOAD_TIMEOUT}")
logging.debug(f"PROXIES_TIMEOUT_LIMIT = {PROXIES_TIMEOUT_LIMIT}")
logging.debug(f"TARGET URL = {URL}")
logging.debug(f"LOGGING CONFIGURATION = {LOG_CONFIG}")


def run_spiders() -> None:
    """
    Used to acquire new proxies.
    """
    system("scrapy crawl arachne -O proxies.json")
    sleep(10)

run_spiders()

def fetch_proxies() -> tuple:
    """
    A generator that returns a tuple (IP, PORT) of a proxy upon iteration.
    """
    with open(PROXY_FILE) as f:
        proxies = load(f)
        shuffle(proxies)
        for proxy in proxies:
            yield proxy["IP Address"], proxy["Port"]


def create_driver(ip: str, port: str, premium = True) -> webdriver.Firefox:
    """
    A function to create a new Firefox driver object
    given the inputs (ip, port) that specify the proxy to use.
    """
    if premium:
        ip = PROXY
        port = 2000
    window_size = choice(RESOLUTIONS).split(',') # choose a random resolution
    firefox_options = webdriver.FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    # setting the profiler to a certain proxy and a random agent
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", ip)
    profile.set_preference("network.proxy.http_port", int(port))
    profile.set_preference("network.proxy.ssl", ip)
    profile.set_preference("network.proxy.ssl_port", int(port))
    profile.set_preference("general.useragent.override", choice(AGENTS))
    profile.set_preference("browser.download.folderList", 2) # prevent automatic downloads
    # setting up the browser options to run headless with enabled JS to allow the site to render
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--enable-javascript")
    driver = webdriver.Firefox(
        options=firefox_options,
        firefox_profile=profile
    )
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT) # set maximum loadout time
    driver.set_window_size(int(window_size[0]), int(window_size[1])) # set the chosen resolution
    return driver

def validate_html(html: str) -> None:
    """
    A function used to validate that the page we fetched
    is not a blocked or a captcha page using css selectors.
    """
    body = HtmlResponse(url=URL, body=html, encoding='utf-8') # get a HTML response object from string to allow parsing
    try: assert not "captcha" in body.css('script[src]::attr(src)').get()
    except TypeError: pass

def parse_html(html: str) -> set:
    """
    A function used to extract the products from the page HTML
    using css selectors.
    """
    body = HtmlResponse(url=URL, body=html, encoding='utf-8')
    ids = []
    imgs = {}
    links = {}
    for tag in body.css("div.product-item-meta[id]"):
        id = tag.css("::attr(id)").get().split('-')[::-1][0]
        ids.append(id)
        img = body.css(f"img#img-{id}")
        link = body.css(f"a#product-item-meta-link-{id}::attr(href)").get()
        links[id] = link
        imgs[id] = {"src": img.css("::attr(src)").get(),
                    "alt": img.css("::attr(alt)").get()}
    return set(ids), imgs, links
    

def main(rest=10):
    """
    The main function to run.
    """
    i = 0
    Port = 20000
    logging.info("Acquiring the proxies list.")
    proxy = fetch_proxies() # create proxies generator
    logging.info("Control loop started.")
    timeout_count = 0 # a counter to count how many timeouts occured and the need to update the proxies
    results = set()
    while True:
        i += 1
        try: ip, port = next(proxy) # get a frexh proxy
        except StopIteration:
            logging.warning("Consumed all existing proxies, acquiring new.")
            timeout_count = 0
            run_spiders()
            proxy = fetch_proxies()
        if timeout_count > PROXIES_TIMEOUT_LIMIT:
            logging.error("Too many timeouts occurred, updating the proxies.")
            timeout_count = 0
            run_spiders()
            proxy = fetch_proxies()
        logging.info(f"Instantiating a driver with proxy: {ip}:{port}.")
        driver = create_driver(PROXY, Port+i, premium=False)
        try:
            logging.info(f"Attempting to get the page.")
            driver.get(URL)
            wait = WebDriverWait(driver, PAGE_DOWNLOAD_TIMEOUT)
            logging.info(f"Validating the page.")
            validate_html(driver.page_source)
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "product-item-name")))
            logging.info("Parsing the page.")
            new_ids, new_imgs, new_links = parse_html(driver.page_source)
            # check if any new products are present
            if (results != new_ids  and
                results != set()):
                new_items = new_ids-results
                if new_items != set():
                    logging.warning(f"New items {new_items} has been found!")
                    send_email(new_items, new_imgs, new_links)
            results = new_ids
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
