from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime

def writeToFile(webpage, append):
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
	file = open("./outputs/"+dt_string+append+".html", "wb")
	file.write(webpage)
	file.close()

webdriver = "/usr/local/bin/chromedriver"
url = 'https://www.pinnacle.com/en/basketball/nba/matchups/'

driver = Chrome(webdriver)
try:
	driver.get(url)
	time.sleep(10)
	ids = len(driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]'))
	for index in range(ids):
		allElements = driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]')
		allElements[index].click()
		time.sleep(5)
		#look for player props
		try:
			props = driver.find_element_by_xpath("//button[contains(text(), 'Player Props')]")
			props.click()
			time.sleep(3)
			webpage = driver.page_source.encode("utf-8")
			writeToFile(webpage, "props")
		except NoSuchElementException:
			matchup = driver.find_elements_by_class_name('style_desktop_textLabel__3KhAQ')[3]
			print('no player props in '+matchup.text)
		webpage = driver.page_source.encode("utf-8")
		# writeToFile(webpage, "matchup")
		driver.back()
		time.sleep(5)
	#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "contentBlock")))
	webpage = driver.page_source.encode("utf-8")
	writeToFile(webpage, "")
finally:
	driver.quit()