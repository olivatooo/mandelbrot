from selenium import webdriver
import sys
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from user_agents import get_random_user_agent
import re
import html2text
import threading
from time import sleep
import datetime
from colors import colors
import json
import signal
import argparse
from selenium.webdriver.common.by import By
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

NUMBER_OF_THREADS = 4
DELAY_TO_START_THREADS = 20
BASE_TARGET = "https://www.ufscar.br"
BASE_DOMAIN = urlparse(BASE_TARGET).netloc
BASE_DOMAIN = BASE_DOMAIN.lstrip("www.")
BASE_DOMAIN = BASE_DOMAIN.split(".")[-2]
MAX_DEPTH = 1
CURRENT_DEPTH = 0
SCROLL_PAUSE_TIME=1
INFINITE_SCROLL=10
STAY_INSIDE_DOMAIN = True
BENCHMARK = False

founds = {}


def benchmark():
    pass


def verify_founds():
    for key in founds:
        if founds[key]["exist"] is False:
            try:
                urlopen(key)
            except HTTPError as e:
                print("HTTP error", e)
            except URLError as e:
                print("Opps ! Page not found!", e)
            else:
                print('Yeah !  found ')


def save_results():
    print(colors.OKGREEN, f"[Saving results to file {BASE_TARGET}_{datetime.datetime.now()}.json]", colors.ENDC)
    f = open(f'./results_{datetime.datetime.now()}.json', 'w')
    f.write(json.dumps(founds))
    f.close()


def add_to_founds(url, level):
    if STAY_INSIDE_DOMAIN:
        if BASE_DOMAIN not in url:
            return
    if url not in founds:
        founds[url] = {"level":  level + 1, "visited" : False, "exist" : False}


def handler(signum, frame):
    print(colors.WARNING, f"[Signal Received... saving results to file] {signum}", colors.ENDC)
    save_results()
    raise SystemExit


def soup_finder(content, url, level):
    global CURRENT_DEPTH
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if "http" not in href:
            href = base_url + href
            add_to_founds(href, level)


def extract_urls(text, level):
    global CURRENT_DEPTH
    plain_text = html2text.html2text(text)
    url_pattern = re.compile(r'\b(?:https?://|www\.)\S+\b')
    matches = re.findall(url_pattern, plain_text)
    for url in matches:
        add_to_founds(url, level)
    if level + 1 > CURRENT_DEPTH:
        CURRENT_DEPTH = level + 1


ANIMATION_INDEX = 0
def progress():
    global ANIMATION_INDEX
    global ANIMATION
    print(colors.OKBLUE, "Processed" ,ANIMATION_INDEX, " found ", len(founds), "max depth processed", CURRENT_DEPTH, colors.ENDC, end='\r')
    ANIMATION_INDEX+=1


def trigger_all_js_events(driver: Chrome):
    all_elements = driver.find_elements(By.XPATH, '//*')
    for element in all_elements:
        try:
            # Trigger JavaScript events using execute_script
            driver.execute_script("arguments[0].scrollIntoView();", element)
            driver.execute_script("arguments[0].click();", element)
            sleep(0.1)
            # Add more JavaScript events as needed
        except Exception as e:
            pass

def dive(target, driver : Chrome, current_level):
    progress()
    founds[target] = {"level": current_level, "visited" : True, "exist" : False}
    try:
        driver.get(target)
        #  trigger_all_js_events(driver)
        founds[target]["exist"] = True
    except Exception as e:
        print(colors.FAIL, "[ERROR]", str(e),colors.ENDC, file=sys.stderr)
        founds[target]["exist"] = False
    soup_finder(driver.page_source, driver.current_url, current_level)
    extract_urls(driver.page_source, current_level)


def scroll_down(driver: Chrome):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def get_next_target():
    for key in founds:
        if founds[key]["visited"] is False and founds[key]["level"] <= MAX_DEPTH:
            founds[key]["visited"] = True
            return key, founds[key]["level"]
    return None, 0

def mandelbrot():
    print(colors.OKCYAN, "[Starting Mandelbrot in Thread]", colors.ENDC , str(threading.current_thread().ident))
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("user-agent="+get_random_user_agent())
    options.add_experimental_option("prefs", {
        "download.default_directory": "/dev/null",  # Set the download directory to /dev/null (Linux) or NUL (Windows)
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
    })
    options.page_load_strategy = "eager"
    driver = Chrome(options=options)
    driver.implicitly_wait(5)
    # Disable any redirection... now that I thinking about maybe this is a problem?
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': "window.onbeforeunload = function(){ return 'Are you sure you want to leave?';};"})
    target, level = get_next_target()
    while target is not None:
        dive(target, driver, level)
        target, level = get_next_target()
    print(colors.OKBLUE, "[No more targets for]", colors.ENDC , str(threading.current_thread().ident))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Mandelbrot',
                    description='Spawns multiple agressive web scrapers to search for urls, and save the results in a json file, with the following structure: {"url": {"level": int, "visited": bool, "exist": bool}}',
                    epilog='Problems suggestions go to: https://github.com/olivato/mandelbrot',)
    parser.add_argument('target', help='Target url to start digging', type=str)
    parser.add_argument('-d', '--depth', help='Maximum depth to search', type=int, default=MAX_DEPTH)
    parser.add_argument('-t', '--threads', help='Number of threads to use', type=int, default=NUMBER_OF_THREADS)
    parser.add_argument('-dtt', '--delay-to-start-threads', help='Delay to start thread swarm', type=int, default=DELAY_TO_START_THREADS )
    parser.add_argument('-ict', '--infinite-scrolling', help='How much times infinite scrolling will be triggered', type=int, default=DELAY_TO_START_THREADS )
    parser.add_argument('-icd', '--infinite-scrolling-delay', help='How much time we should wait between each scroll', type=int, default=DELAY_TO_START_THREADS )
    parser.add_argument('-s', '--stay-domain', help='If true, we will stay in the same domain', type=bool, default=True)
    parser.add_argument('-v', '--verify', help='If true, we will verify if the found url exists', type=bool, default=False)
    parser.add_argument('-b', '--benchmark', help='If true, we will benchmark the run, this forcefully implies -v', type=bool, default=False)
    args = parser.parse_args()
    BASE_TARGET = args.target
    MAX_DEPTH = args.depth
    NUMBER_OF_THREADS = args.threads
    DELAY_TO_START_THREADS = args.delay_to_start_threads

    signal.signal(signal.SIGINT, handler)
    print(colors.OKGREEN, colors.BOLD, "[Starting mandelbrot dive...]", colors.ENDC, "target :", BASE_TARGET)
    threads = []
    founds[BASE_TARGET] = {"level": 0, "visited" : False, "exist" : False}
    for i in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=mandelbrot)
        t.start()
        threads.append(t)
        if i == 0:
            print(colors.WARNING, colors.BOLD, f"Waiting {DELAY_TO_START_THREADS} seconds to start threads... Increase this value if the program terminates early", colors.ENDC)
            sleep(DELAY_TO_START_THREADS)

    for t in threads:
        t.join()

    save_results()

