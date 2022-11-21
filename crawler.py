## Import Package
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

import requests
import time
import os
import re


load_dotenv()


def getStockWeight():
    index_count = 20
    res = requests.get('https://www.taifex.com.tw/cht/2/weightedPropertion')
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.findChildren('table')[0].findChildren('tr')
    notify_message = ''

    for i in range(1, index_count+1):
        element = rows[i].findChildren('td')
        notify_message += f'\n{element[1].text.strip()} {element[2].text.strip()}     {element[3].text.strip()}'

    message_object = {
        'message': f'台股權值前{index_count}檔: {notify_message}',
        'webhook': os.environ.get("line-notify-stocker")
    }
    pushLineNotify(message_object)


def getFutureDayDiff():
    driver = getChromeDriver()
    driver.get("https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/FuturesDomestic/")
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, 'btn').click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    td = soup.find_all("tbody")[0].find_all("tr")[1].find_all("td")
    difference = float(td[11].text.replace(',', '')) - float(td[12].text.replace(',', ''))
    message_object = {
            'message': f'商品: {td[0].text.strip()}, 成交價: {td[6].text}, 漲跌: {td[7].text}, 震幅: {td[8].text}, 點數差: {difference}, 最高: {td[11].text}, 最低: {td[12].text}',
        'webhook': os.environ.get("line-notify-stocker")
    }
    pushLineNotify(message_object)


def crawlTodayCorporateBriefingSession(exchange_type, dateTime_in):
    current_time = datetime.now()
    url = "https://mops.twse.com.tw/mops/web/ajax_t100sb02_1"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {
        "step": 1,
        "firstin": 1,
        "TYPEK": exchange_type,
        "year": dateTime_in.year-1911,
        "month": dateTime_in.month
    }
    res = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.findChildren('table')[0].findChildren('tr')
    current_date = f'{dateTime_in.year-1911}/{dateTime_in.month}/{dateTime_in.day}'
    message = ""
    for i in range(2, len(rows)):
        cells = rows[i].findChildren('td')
        if not cells:
            continue
        if re.match('^[0-9]{3}\/[0-9]{2}\/[0-9]{2}$', str(cells[2].text)):
            if cells[2].text == current_date:
                message += f'{cells[0].text} {cells[1].text} {cells[2].text} {cells[4].text.strip()}\n'
        else:
            date_range = cells[2].text.split(' 至 ')
            opening_day = date_range[0].split('/')
            opening_day[0] = str(int(opening_day[0]) + 1911)
            opening_day = datetime.strptime('-'.join(opening_day), '%Y-%m-%d')
            closing_day = date_range[1].split('/')
            closing_day[0] = str(int(closing_day[0]) + 1911)
            closing_day = datetime.strptime('-'.join(closing_day), '%Y-%m-%d')+ timedelta(days=1)
            if opening_day < dateTime_in < closing_day:
                message += f'{cells[0].text} {cells[1].text} {cells[2].text} {cells[4].text.strip()}\n'

    return message


def getTodayCorporateBriefing():
    current_time = datetime.now()
    message = f'{current_time.year-1911}/{current_time.month}/{current_time.day} 法說會公司\n'
    for exchange_type in ['sii', 'otc']:
        message += crawlTodayCorporateBriefingSession(exchange_type, current_time)
    message_object = {
        'message': message,
        'webhook': os.environ.get("line-notify-stocker")
    }
    pushLineNotify(message_object)


def getChromeDriver():
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    service_object = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service_object, options=option)


def pushLineNotify(message_object):
    notifyUrl = 'https://notify-api.line.me/api/notify'

    headers = {
        'Authorization': f'Bearer {message_object["webhook"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        "message": message_object['message']
    }

    res = requests.post(notifyUrl, headers=headers, data=payload)
    print(res.text)


if __name__ == '__main__':
    getTodayCorporateBriefing()

