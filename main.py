"""
ccn-coverage-scraper
"""
import logging

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logger = logging.getLogger('uvicorn')
logger.setLevel(logging.DEBUG)

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/plans")
def scrape_website(zip_5: str, state: str="", cityname: str="", primary: str="", street_number: str="", st: str="", post_direction: str=""):
    # these variables can be made from previous variable being mashed together
    #state_cap = str.upper(state)
    #cityname_cap = str.capitalize(cityname)
    #street_name = f'{primary}%20{street_number}%20{st}%20{post_direction}'
    #zip_95 = zip_5
    #url = f"https://www.allconnect.com/local/{state}/{cityname}?city={cityname_cap}&primary={primary}&street_line={street_name}&street={street_number}%20{st}&postDirection={post_direction}&state={state_cap}&zip9={zip_95}&zip5={zip_5}&zip9or5={zip_95}&prettyAddress={primary}%20{street_number}%20{st}%20{post_direction}%2C%20{cityname_cap}%2C%20{state_cap}%20{zip_95}&zip={zip_95}"

    allconnect_url = f'https://www.allconnect.com/results/providers?zip={zip_5}'
    logger.info(f"invoking url: {allconnect_url}")
    try:
        wifi_providers = get_plans(allconnect_url)
        return wifi_providers
    except:
        logger.exception(f"error logging {allconnect_url}")


def get_plans(url: str) -> dict:
    # now everything gets packaged together
    wifi_providers = {}
    driver = None
    try:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5) # 5 second timeout

        driver.get(url)

        li_elements = driver.find_elements(By.CSS_SELECTOR, r"li.mb-16.md\:mb-24.last\:mb-0")

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
    except requests.RequestException as e:
        logger.exception("request error")
        raise HTTPException(status_code=500, detail="Failed to fetch URL") from e
    except Exception as e:
        logger.exception("general exception")
        raise HTTPException(status_code=500, detail="Failed to scrape website") from e
    finally:
        if driver:
            driver.quit()
    return wifi_providers


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
