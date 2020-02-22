from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import schedule
import time
from datetime import datetime
import sys

def writeToFile(webpage, append):
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
	file = open("./outputs/"+dt_string+append+".html", "wb")
	file.write(webpage)
	file.close()

webdriver = "/usr/local/bin/chromedriver"
url = 'https://www.pinnacle.com/en/basketball/nba/matchups/'

def scrape():
	driver = Chrome(webdriver)
	try:
		driver.get(url)
		time.sleep(15)
		# decimal = driver.find_element_by_xpath("//i[contains(text(), 'Decimal Odds')]")
		decimal = driver.find_element_by_xpath('//*[contains(@class, "style_dropdown")]')
		decimal.click()
		time.sleep(1)
		american = driver.find_element_by_xpath("//a[contains(text(), 'American Odds')]")
		american.click()
		time.sleep(1)
		ids = len(driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]'))
		for index in range(ids):
			allElements = driver.find_elements_by_xpath('//a[@data-test-id="Event.MarketCnt"]')
			try:
				allElements[index].click()
			except IndexError:
				print('index error: '+str(index))
				break
			time.sleep(3)
			#look for player props
			matchup = driver.find_element_by_xpath("//span[contains(text(), 'vs.')]")
			try:
				props = driver.find_element_by_xpath("//button[contains(text(), 'Player Props')]")
				props.click()
				time.sleep(3)
				# webpage = driver.page_source.encode("utf-8")
				# writeToFile(webpage, "props")
			except NoSuchElementException:
				print('no player props in '+matchup.text)
				driver.back()
				time.sleep(3)
				continue
			fullLines = driver.find_elements_by_xpath('//*[contains(@class, "style_marketGroup")]')
			# labelAndOdds = driver.find_elements_by_class_name('style_content__20TF7')
			now = datetime.now()	
			dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
			file = open("./outputs/"+dt_string+matchup.text+".csv", "w+")
			for idx in range(len(fullLines)):
				try:
					line = fullLines[idx].find_elements_by_xpath('//*[contains(@class, "style_title")]')[idx]
					labels = fullLines[idx].find_elements(By.CLASS_NAME, 'label')
					prices = fullLines[idx].find_elements(By.CLASS_NAME, 'price')
					file.write(line.text+","+labels[0].text+","+prices[0].text+","+labels[1].text+","+prices[1].text+"\n")
				except NoSuchElementException:
					print('line '+idx+' is locked in '+matchup)
					continue
			file.close()
			driver.back()
			time.sleep(3)
		#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "contentBlock")))
		# webpage = driver.page_source.encode("utf-8")
		# writeToFile(webpage, "")
	finally:
		driver.quit()

if len(sys.argv) > 1:
	schedule.every().day.at(sys.argv[1]).do(scrape)
	while True:
	    schedule.run_pending()
	    time.sleep(60) # wait one minute
else:
	scrape()

