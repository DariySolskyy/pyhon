import re
import csv

import ujson as json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Define credectials in creds.py
from creds import username, password

from time import sleep

# Spyder to search and scrap Facebook user ID based on users CSV list 
class FacebookBot():
    def __init__(self):
        # options = ChromeOptions()
        # options.headless = True
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--no-sandbox")
        # driver = Chrome(options=options)

        # yield driver

        # self.driver = webdriver.Chrome()
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def login(self):
        self.driver.get('https://facebook.com')

        in_email = self.driver.find_element_by_xpath('//*[@id="email"]')
        in_email.send_keys(username)

        in_pwd = self.driver.find_element_by_xpath('//*[@id="pass"]')
        in_pwd.send_keys(password)

        in_btn = self.driver.find_element_by_xpath('//*[@id="loginbutton"]')
        in_btn.click()

        sleep(8)

        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def search(self, src_key):
        try:
            self.driver.get(
                'https://www.facebook.com/search/people/?q=' + src_key + '&filters=eyJjaXR5Ijoie1wibmFtZVwiOlwidXNlcnNfbG9jYXRpb25cIixcImFyZ3NcIjpcIjEwODQyNDI3OTE4OTExNVwifSIsImZyaWVuZHNfb2ZfZnJpZW5kcyI6IntcIm5hbWVcIjpcInVzZXJzX2ZyaWVuZHNfb2ZfZnJpZW5kc1wiLFwiYXJnc1wiOlwiXCJ9In0%3D')
            sleep(2)
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

            usr_id = self.driver.execute_script(
                "return JSON.parse(document.getElementById('initial_browse_result').querySelector('[data-xt]').getAttribute('data-xt').match(/\{(.*?)\}/)[0]).unit_id_result_id;")
        except:
            usr_id = 'Not found'

        return usr_id

with open('FB_ID_Document.csv', 'r') as csvinput:
    with open('FB_ID_Document_result.csv', 'w') as csvoutput:
        w = csv.writer(csvoutput, lineterminator='\n')
        r = csv.reader(csvinput)

        bot = FacebookBot()
        bot.login()

        items = []

        for item in r:
            # search by Full name
            src_key = item[0].replace(' ', '%20')

            # search by Email
            # src_key = item[3]
            item.append(bot.search(src_key))
            print(item)

            items.append(item)

        w.writerows(items)
