from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime

webdriver = "/usr/local/bin/chromedriver"
url = 'https://www.pinnacle.com/en/basketball/nba/matchups/'

driver = Chrome(webdriver)
try:
	driver.get(url)
	time.sleep(15)
	ids = len(driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]'))
	for index in range(ids):
		allElements = driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]')
		allElements[index].click()
		#look for player props
		time.sleep(5)
		driver.back()
		time.sleep(5)
	#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "contentBlock")))
	webpage = driver.page_source.encode("utf-8")
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
	file = open("./outputs/"+dt_string+".html", "wb")
	file.write(webpage)
	file.close()
finally:
	driver.quit()
