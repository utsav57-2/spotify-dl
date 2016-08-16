from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from urllib import quote_plus as qp
import urllib2
from bs4 import BeautifulSoup

class Scraper:

    def __init__(self,display=False,base_link='www.youtube.com',debug=False):
        self._display = display
        self._debug = debug
        self._base_link = base_link

        if display:
            self._driver = webdriver.Firefox()
        else:
            self._driver = webdriver.PhantomJS()


    def __del__(self):
        self._driver.quit()

    def is_relative(link):
        if '.com' in link:
            return Flase

        else:
            return True

    def get_youtube_link(self,song):

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


    def get_download_link(self,song):
        yt_link = self._base_link + self.get_youtube_link(song)
        self._driver.get('http://www.youtube-mp3.org/')
        text_box = self._driver.find_element_by_id('youtube-url')
        text_box.clear()
        text_box.send_keys(yt_link)

        submit_button = self._driver.find_element_by_id('submit')
        submit_button.send_keys(Keys.ENTER)

        # spend maximum of 10 seconds on a single link
        link_div = None
        no_of_tries = 0
        while not link_div and no_of_tries < 10:
            try:
                link_div = self._driver.find_element_by_id('dl_link')
            except selenium.common.exceptions.NoSuchElementException:
                no_of_tries += 1
                time.sleep(1)


        if not link_div:
            return None

        links = link_div.find_elements_by_tag_name('a')
        links = [i.get_attribute('href') for i in links]
        return max(links)
