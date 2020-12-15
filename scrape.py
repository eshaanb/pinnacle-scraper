from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
from datetime import datetime
import sys
import os
import subprocess
import pdb


PHONE_NUMBER = 'eshaan55@gmail.com'

def writeToFile(webpage, append):
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
	file = open("./outputs/"+dt_string+append+".html", "wb")
	file.write(webpage)
	file.close()

url = 'https://www.pinnacle.com/en/football/nfl/matchups'

def _notify(msg):
	_send_macos_notification(msg)
	_send_imessage(msg)

def _send_macos_notification(msg):
	os.system(f'osascript -e \'display notification "{msg}"\'')

def _send_imessage(msg):
	cmd = f'osascript -e \'tell application "Messages" to send "{msg}" to buddy "{PHONE_NUMBER}"\''
	subprocess.call(cmd, shell=True)

def scrape():
	driver = Chrome(ChromeDriverManager().install())
	bookieDict = {}
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
		ids = len(driver.find_elements_by_xpath('//a[@data-test-id="Event.GameInfo"]'))
		for index in range(ids):
			allElements = driver.find_elements_by_xpath('//a[@data-test-id="Event.GameInfo"]')
			try:
				driver.execute_script("arguments[0].click();", allElements[index])
			except:
				print('error clicking: '+str(index))
				continue
			time.sleep(3)
			#look for player props
			try:
				matchup = driver.find_element_by_xpath("//span[contains(text(), 'vs.')]")
			except NoSuchElementException: 
				print('couldn\'t find matchup for '+str(index))
				driver.back()
				time.sleep(3)
				continue
			try:
				props = driver.find_element_by_xpath("//button[contains(text(), 'Player Props')]")
				driver.execute_script("arguments[0].click();", props)
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
					parts = fullLines[idx].text.split("\n")
					# labels = fullLines[idx].find_elements(By.CLASS_NAME, 'label')
					# prices = fullLines[idx].find_elements(By.CLASS_NAME, 'price')
					# pdb.set_trace()
					overidentifier = matchup.text+parts[0]+parts[1]
					underidentifier = matchup.text+parts[0]+parts[3]
					firstOddsValue = int(parts[2])
					secondOddsValue = int(parts[4])
					if (overidentifier in bookieDict):
						if (abs(bookieDict[overidentifier][0]-firstOddsValue) > 30):
							_notify('difference for '+overidentifier+' has changed from '+bookieDict[overidentifier][0]+' to '+firstOddsValue)
						elif (abs(bookieDict[overidentifier][1]-firstOddsValue) > 30):
							_notify('difference for '+overidentifier+' has changed from '+bookieDict[overidentifier][1]+' to '+firstOddsValue)
						bookieDict[overidentifier] = (min(firstOddsValue, bookieDict[overidentifier][0]), max(parts[2], bookieDict[overidentifier][1]))
					else:
						bookieDict[overidentifier] = (firstOddsValue, firstOddsValue)

					if (underidentifier in bookieDict):
						if (abs(bookieDict[underidentifier][0]-secondOddsValue) > 30):
							_notify('difference for '+underidentifier+' has changed from '+str(bookieDict[underidentifier][0])+' to '+str(secondOddsValue))
						elif (abs(bookieDict[underidentifier][1]-secondOddsValue) > 30):
							_notify('difference for '+underidentifier+' has changed from '+str(bookieDict[underidentifier][1])+' to '+str(secondOddsValue))
						bookieDict[underidentifier] = (min(secondOddsValue, bookieDict[underidentifier][0]), max(secondOddsValue, bookieDict[underidentifier][1]))
					else:
						bookieDict[underidentifier] = (secondOddsValue, secondOddsValue)
					file.write(parts[0]+","+parts[1]+","+parts[2]+","+parts[3]+","+parts[4]+"\n")
				except (NoSuchElementException, IndexError):
					print('line '+str(idx)+' is locked/missing in '+matchup.text)
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
	schedule.every(int(sys.argv[1])).minutes.do(scrape)
	while True:
	    schedule.run_pending()
	    time.sleep(60) # wait one minute
else:
	scrape()

