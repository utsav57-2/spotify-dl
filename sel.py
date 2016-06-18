from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

DISPLAY = False

def init_driver():
    if DISPLAY:
        driver = webdriver.Firefox()
    else:
        driver = webdriver.PhantomJS() # or add to your PATH
    return driver

def get_dl_link(driver,yt_link):
    driver.get('http://www.youtube-mp3.org/')
    text_box = driver.find_element_by_id('youtube-url')
    text_box.clear()
    text_box.send_keys(yt_link)

    submit_button = driver.find_element_by_id('submit')
    submit_button.send_keys(Keys.ENTER)
    # time.sleep(10)

    link_div = None
    no_of_tries = 0
    while not link_div and no_of_tries < 10:
        try:
            link_div = driver.find_element_by_id('dl_link')
        except selenium.common.exceptions.NoSuchElementException:
            no_of_tries += 1
            time.sleep(1)


    if not link_div:
        # handle exception

    links = link_div.find_elements_by_tag_name('a')
    links = [i.get_attribute('href') for i in links]
    return max(links)


def close_driver(driver):
    driver.quit()
