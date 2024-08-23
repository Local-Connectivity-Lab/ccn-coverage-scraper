#!/usr/bin/env python3
# A test document for sorting of webscraped info

import json
import logging
import time
import urllib.parse

import lxml
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5) # 5 seconds wait

test_url = "https://www.allconnect.com/local/va/mechanicsville?city=Mechanicsville&primary=7065&street_line=7065%20Ann%20Cabell%20Ct&street=Ann%20Cabell%20Ct&point=%7B%22latitude%22%3A37.592567%2C%22longitude%22%3A-77.355141%7D&state=VA&streetLine=7065%20Ann%20Cabell%20Ct&zip5=23111&zip9or5=23111&prettyAddress=7065%20Ann%20Cabell%20Ct%2C%20Mechanicsville%2C%20VA%2023111&zip=23111-5227"
driver.get(test_url)

li_elements = driver.find_elements(By.CSS_SELECTOR, r"li.mb-16.md\:mb-24.last\:mb-0")

wifi_providers = {}

# Extracting information for each provider and adding it to the dictionary
for elem in li_elements:
    provider_name = elem.find_element(By.CSS_SELECTOR, "p.text-12")

    if provider_name:
        provider_name = provider_name.text
        provider_details = {}

        provider_speed = elem.find_element(By.CSS_SELECTOR, r"div.details__container")
        details = [s.strip() for s in provider_speed.text.split('\n')]
        provider_details['Available speeds'] = details[1]
        provider_details['Contract length'] = details[3]
        provider_details['Connection type'] = details[5]

        provider_price = elem.find_element(By.CSS_SELECTOR, r"div.flex.items-start")
        prices = [s.strip() for s in provider_price.text.split('\n')]
        # processing price string to format
        if prices[1].startswith("/"):
            # no cents, add ".00"
            priceV = prices[0] + ".00" + prices[1]
        else:
            priceV = prices[0] + "." + prices[1]
        provider_details["Starting at"] = priceV

        wifi_providers[provider_name] = provider_details
    else:
        print(f"no provider found for {elem.get_attribute('innerHTML')}")

# Printing the dictionary
print(wifi_providers)

#filename = "data.json"
#with open(filename, 'w') as json_file:
#    json.dump(wifi_providers, json_file, indent=4)
