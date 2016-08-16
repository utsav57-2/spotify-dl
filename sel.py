from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from urllib import quote_plus as qp

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

    # spend maximum of 10 seconds on a single link
    link_div = None
    no_of_tries = 0
    while not link_div and no_of_tries < 10:
        try:
            link_div = driver.find_element_by_id('dl_link')
        except selenium.common.exceptions.NoSuchElementException:
            no_of_tries += 1
            time.sleep(1)


    if not link_div:
        return None

    links = link_div.find_elements_by_tag_name('a')
    links = [i.get_attribute('href') for i in links]
    return max(links)


def get_dl_list(pl,base_url=None):
    driver = init_driver()
    for sng in pl:
        dl_link = get_dl_link(driver,base_url + sng['yt_link'])

        # TODO
        if not dl_link:
            pass

        sng['dl_link'] = dl_link

    close_driver(driver)




def close_driver(driver):
    driver.quit()




class Scraper:

    def __init__(self,display=False,base_link='www.youtube.com',debug=False):
        self._display = display
        self._debug = debug
        self._base_link = base_link

        if display:
            self._driver = webdriver.Firefox()
        else:
            self._driver = webdriver.PhantomJS() # or add to your PATH


    def __del__(self):
        self._driver.quit()

    def is_relative(link):
        if '.com' in link:
            return Flase

        else:
            return True

    def get_youtube_link(song):

        base_url = "https://www.youtube.com/results?search_query="
        query = qp(song["full_identifier"])
        req_url = base_url + query

        if self._debug:
            print 'Search Query: ' + req_url

        result = urllib2.urlopen(req_url)
        html = result.read()
        soup = BeautifulSoup(html,"lxml")

        links = soup.find_all('h3',class_='yt-lockup-title')
        # TODO scrape title
        title_texts = [link.a.string for link in links]

        if self._debug:
            print "\nLINK TITLES\n"
            for title in title_texts:
                print title,type(title)

        links_arr = [link.a['href'] for link in links]

        if self._debug:
            print "\nLINKS\n"
            for link in links_arr:
                print link,type(link)

        return links_arr[0]


    def get_download_link(song):
        yt_link = self._base_link + self.get_youtube_link(song)
        self._driver.get('http://www.youtube-mp3.org/')
        text_box = driver.find_element_by_id('youtube-url')
        text_box.clear()
        text_box.send_keys(yt_link)

        submit_button = driver.find_element_by_id('submit')
        submit_button.send_keys(Keys.ENTER)

        # spend maximum of 10 seconds on a single link
        link_div = None
        no_of_tries = 0
        while not link_div and no_of_tries < 10:
            try:
                link_div = driver.find_element_by_id('dl_link')
            except selenium.common.exceptions.NoSuchElementException:
                no_of_tries += 1
                time.sleep(1)


        if not link_div:
            return None

        links = link_div.find_elements_by_tag_name('a')
        links = [i.get_attribute('href') for i in links]
        return max(links)
