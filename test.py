#A test document for sorting of webscraped info

from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
import urllib.parse
import lxml
import json

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

test_url = "https://www.allconnect.com/local/va/mechanicsville?city=Mechanicsville&primary=7065&street_line=7065%20Ann%20Cabell%20Ct&street=Ann%20Cabell%20Ct&point=%7B%22latitude%22%3A37.592567%2C%22longitude%22%3A-77.355141%7D&state=VA&streetLine=7065%20Ann%20Cabell%20Ct&zip5=23111&zip9or5=23111&prettyAddress=7065%20Ann%20Cabell%20Ct%2C%20Mechanicsville%2C%20VA%2023111&zip=23111-5227"
driver.get(test_url)
time.sleep(5)

html_text = driver.page_source

soup = BeautifulSoup(html_text, 'lxml')
li_elements = soup.find_all('li', class_='mb-16 last:mb-0')
scrap_data = '\n'.join([li.text for li in li_elements])

wifi_providers = {}

# Extracting information for each provider and adding it to the dictionary
for li in li_elements:
    provider_name = li.find('span', class_='text-10 leading-10 md:ml-16 lg:ml-0 lg:mb-8').text
    print(provider_name)
    provider_details = {}

    provider_speed = li.find(class_='product__info-box relative border-b border-solid border-gray-bg-dark px-16 py-10 md:p-16 md:flex md:justify-between md:pr-0 md:pl-16 md:py-0 lg:pl-24 lg:py-24 items-start md:w-1/2 lg:w-1/4').text
    speedQ, speedV = 'Available speeds',provider_speed[16:]
    provider_details[speedQ] = speedV

    provider_price = li.find(class_='text-gray-steel text-24 md:text-18 lg:text-28 leading-28 m-0').text
    priceQ, priceV = 'Starting at', provider_price
    provider_details[priceQ] = priceV

    wifi_providers[provider_name] = provider_details

# Printing the dictionary
print(wifi_providers)

filename = "data.json"
with open(filename, 'w') as json_file:
    json.dump(wifi_providers, json_file, indent=4)
