"""
ccn-coverage-scraper
"""
#import traceback
from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fastapi.middleware.cors import CORSMiddleware
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import TimeoutException
#from selenium.webdriver.common.by import By
import time
#import urllib.parse
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
@app.get("/")
def scrape_website(state: str, cityname: str, primary: str, street_number: str, st: str, post_direction: str, zip_5: str):

    # these variables can be made from previous variable being mashed together
    state_cap = str.upper(state)
    cityname_cap = str.capitalize(cityname)
    street_name = f'{primary}%20{street_number}%20{st}%20{post_direction}'
    #zip_95 = f'{zip_5}-{zip_9}'

#"https://www.allconnect.com/local/{state}/{cityname}?city={cityname_cap}&primary={primary}&street_line={street_name}&street={street_number}%20{st}&postDirection={post_direction}&state={state_cap}&zip9={zip_95}&zip5={zip_5}&zip9or5={zip_95}&prettyAddress={primary}%20{street_number}%20{st}%20{post_direction}%2C%20{cityname_cap}%2C%20{state_cap}%20{zip_95}&zip={zip_95}"
    try:
    # now everything gets packaged together
        # Modify alconnect_url for the next attempt
        alconnect_url = f'https://www.allconnect.com/results/providers?zip={zip_5}'
        print("stage 2", alconnect_url)
        # wifi_providers = get_plans(alconnect_url, 'mb-16 md:mb-24 last:mb-0')
        wifi_providers = get_plans(alconnect_url, 'mb-16 last:mb-0')
        return wifi_providers
    except:
        print("no work")
def get_plans(alconnect_url: str, li_elementclass: str ) -> dict:
    # now everything gets packaged together
    wifi_providers = {}
    try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            #this is all of the parameters that are being used to test the url
            '''
            state = 'va'
            cityname= 'arlington'
            primary = '3109'
            street_number = '9th'
            st = "St"
            post_direction = 'N'
            zip_5 = '22201'
            '''
            #this is the url you type into chrome: http://127.0.0.1:8000/?url=https://www.allconnect.com&state=va&cityname=arlington&primary=3109&street_number=9th&st=St&post_direction=N&zip_5=22201&zip_9=2024

            #selenium starts up and gets driver page source
            driver.get(alconnect_url)
            time.sleep(3)
            '''
            try:
                # Wait until the element with class "mb-16" appears
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.title-card')))
                print("Element found!")
            except TimeoutException:
                print("Timed out waiting for element")
            '''
            html_text = driver.page_source
            #beautiful soup finds the relevant data
            soup = BeautifulSoup(html_text, 'lxml')
            li_elements = soup.find_all('li', class_=li_elementclass)
            if len(li_elements) == 0:
                print("no prices found")
            scrap_data = '\n'.join([li.text for li in li_elements])

            # Extracting information for each provider and adding it to the dictionary
            for li in li_elements:
                provider_name = li.find('span', class_='text-10 leading-10 md:ml-16 lg:ml-0 lg:mb-8')
                if provider_name:
                    provider_name = provider_name.text
                    print(provider_name)
                    provider_details = {}

                    provider_speed = li.find(
                        class_='product__info-box relative border-b border-solid border-gray-bg-dark px-16 py-10 md:p-16 md:flex md:justify-between md:pr-0 md:pl-16 md:py-0 lg:pl-24 lg:py-24 items-start md:w-1/2 lg:w-1/4').text
                    speedQ, speedV = 'Available speeds', provider_speed[12:]
                    provider_details[speedQ] = speedV

                    provider_price = li.find(class_='text-gray-steel text-24 md:text-18 lg:text-28 leading-28 m-0').text
                    priceQ, priceV = 'Starting at', provider_price
                    provider_details[priceQ] = priceV

                    wifi_providers[provider_name] = provider_details
            # Check if wifi_providers is empty

        # Printing the dictionary
    except requests.RequestException as e:
        #print(e, "1", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to fetch URL") from e
    except Exception as e:
        #print(e, "2", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to scrape website") from e
    finally:
        driver.quit()
    return wifi_providers
