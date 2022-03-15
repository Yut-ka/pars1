import sys
print(sys.stdout.encoding)
sys.stdout.reconfigure(encoding='utf-8')
print(sys.stdout.encoding)
from unittest import main
from matplotlib import container
from numpy import block
from parso import parse
import requests
import bs4
import logging
import collections
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import csv

logging.basicConfig()
logger = logging.getLogger("wix")

ParseResult = collections.namedtuple(
    'ParseResul',
    (
        'brand_name',
        'goods_name',
        'url'
    )
)


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36", "Content-Type":"text"}
        self.result = []
    
    def load_page(self, url:str):
        res = self.session.get(url=url, timeout=30, headers=self.header)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, "lxml")
        container = soup.select("li[data-hook='product-list-grid-item']")
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):

        logger.info(block)
        logger.info('=' * 100)

        url_block = block.select_one('a')
        if not url_block:
            logger.error('no_url_block')
            return
        
        url = url_block.get('href')
        if not url:
            logger.error('no_url')
            return
        
        executable_path = 'C:\webdriver'
        chrome_options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(executable_path="webdriver\\chromedriver.exe")
        driver.implicitly_wait(30)
        driver.get(url)
        ul = driver.find_element_by_css_selector("pre._28cEs ul")
        description = driver.find_element_by_css_selector("pre._28cEs")
        img = driver.find_elements_by_css_selector("img.H5gG5")
        try:
            video = driver.find_element_by_css_selector("div.screen__screen___3BN2N video")
            video_url = "no_video"

            if(video != None):
                video_url = video.get_attribute('src')
        except:
            video_url = "no_video"
            print('no_video')
        

        #print(description.text)
        #print(img[0].get_attribute('src'))
        images = ""
        for a in img:
            src = a.get_attribute('src')
            text_until_jpg = src[:src.find(".jpg")+4]
            images += text_until_jpg + ", "
        images = images[:-2]        
        
        

        #driver.quit()
        
        text2 = self.load_page(url)
        soup2 = bs4.BeautifulSoup(text2, "lxml")

        title = soup2.select_one("h1")
        title_text = title.text

        SKU = soup2.select_one("div._1rwRc")
        SKU_text = SKU.text[9:]

        price = soup2.select_one("div._26qxh span:nth-child(1)")
        price_text = price.text[:-2]


        with open('day.csv', 'a', newline='') as f:
            f.write(title_text + ", " + SKU_text + ", " + price_text.replace(",",".") + ", " + "\"" + description.text.replace("\"","") + "\""  + ", " + "\"" + images + "\"" + ", " + "\"" + video_url + "\"" + ", День Святого Валентина" +"\n")

        #print(title_text + ", " + SKU_text + ", " + price_text)

    def run(self, url:str):
        text = self.load_page(url)
        self.parse_page(text=text)


if __name__ == '__main__':
    parser = Client()
    parser.run("https://www.embroplace.com/ru/valentine-s-day?currency=")
