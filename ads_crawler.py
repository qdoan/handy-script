#!/usr/bin/python
from time import gmtime, strftime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')
TIME_OUT = 15

def wait(driver,delay):
	try:
		element_present = EC.presence_of_element_located((By.ID, 'element_id'))
		WebDriverWait(driver, delay).until(element_present)
	except TimeoutException:
		pass
	except NoSuchElementException:
		pass

def process_window(driver):
	metas = driver.find_elements_by_tag_name("meta")
	json  = "{"
	json += 'url:"' + driver.current_url +'"'
	json += ', title:"' + driver.title + '"'
	json += ', meta:['
	first = True
	for meta in metas:
		attr = meta.get_attribute('name')
		if attr == None :
			attr = meta.get_attribute('property')

		content = meta.get_attribute('content')
		if content == None:
			content = meta.get_attribute('description')

		if attr == None or content == None or len(attr) == 0 or len(content) == 0:
			continue
		if first:
			first = False
		else:
			json += ","		

		if ("title" in attr) or ("description" in attr) or ("keyword" in attr):
			json += '{attribute:"'+attr+'", content:"'+content+'"}'				
	json += ']}'
	return json

def crawl(url,driver, writer):
	driver.get(url)
	wait(driver,TIME_OUT)
	iframes = driver.find_elements_by_tag_name("iframe")
	main_window = driver.window_handles[0]
	main_url = driver.current_url
	
	for iframe in iframes:
		try:
			iframe.click()
			json_content = ""	
			if len(driver.window_handles) < 2:
				if driver.current_url == main_url:
					continue
				ads_window = driver.window_handles[0]
				json_content = process_window(driver)
				if driver.current_url != main_url:
					driver.get(main_url)
			else:
				ads_window = driver.window_handles[1]
				driver.switch_to_window(ads_window)
				wait(driver,TIME_OUT)
				json_content = process_window(driver)
				driver.close()
				driver.switch_to_window(main_window)
			writer.write(json_content)
			writer.write("\n")
		except ElementNotVisibleException:
			pass

	
if __name__ == "__main__":
	driver = webdriver.Firefox()
	news_urls = ["http://vnexpress.net", "http://dantri.com.vn", "http://vietnamnet.vn", "http://thanhnien.vn", "http://tuoitre.vn", "http://ngoisao.net"]

	#news_url = "http://vietbao.vn"
	#news_url = "http://kenh14.vn"
	#news_url = "http://go.vn"
	#news_url = "http://www.yan.vn"
	#news_url = "http://www.24h.com.vn"
	folder_path = "/home/quydm/Datasets/AdsCrawled/"
	filename = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ".json"
	with open(folder_path+filename,"w") as writer:
		for url in news_urls:
			crawl(url,driver,writer)

	driver.close()
	driver.quit()





