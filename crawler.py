## Import Package
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import requests
import time
import os


load_dotenv()

option = webdriver.ChromeOptions()
option.add_argument('--headless')
option.add_argument('--disable-gpu')
service_object = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service_object, options=option)


def getFutureDayDiff():
    driver.get("https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/FuturesDomestic/")
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, 'btn').click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    td = soup.find_all("tbody")[0].find_all("tr")[1].find_all("td")
    message_object = {
        'message': f'商品: {td[0].text.strip()}, 成交價: {td[6].text}, 漲跌: {td[7].text}, 震幅: {td[8].text}, 最高: {td[11].text}, 最低: {td[12].text}',
        'webhook': os.environ.get("line-notify-stocker")
    }
    pushLineNotify(message_object)


def pushLineNotify(message_object):
    notifyUrl = 'https://notify-api.line.me/api/notify'

    headers = {
        'Authorization': f'Bearer {message_object["webhook"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        "message": message_object['message']
    }

    requests.post(notifyUrl, headers=headers, data=payload)


getFutureDayDiff()