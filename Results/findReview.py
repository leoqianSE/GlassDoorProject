#Given a company's name (input names from a csv file, one name each row), 
#find the first review page url and the last number. Put name, url, pagenumber
#in output csv file. if the company name in the url is not 
#the same as csv input file, a warning is added at the end of the same row

import csv
from gdtool import setupChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from datetime import datetime
import math
import time


def findCompany(companyToSearch, in_driver):
    returnList=[]
    try:
        # 1. open website
        in_driver.get("https://www.glassdoor.com/Reviews/index.htm")
        time.sleep(2)

        # 2. find search box (by name attribute)
        search_box = in_driver.find_element(By.NAME, 'typedKeyword')
        time.sleep(4.2)
        # 3. type search text
        search_box.send_keys(companyToSearch)
    
        # 4. press ENTER
        #search_box.send_keys(Keys.RETURN)
        #search_box.send_keys(Keys.ARROW_DOWN)
        time.sleep(3)
        search_box.send_keys(Keys.ENTER)
        
        # 5. wait for results to load
        time.sleep(3)  # better: use WebDriverWait
        targetPages = in_driver.find_elements(By.CSS_SELECTOR, 'a[class^="employer-card_employerCardContainer"]')
        print(len(targetPages))
        pagelist=[]
        for a in targetPages:
            pagelist.append(a.get_attribute("href"))
        
        
        for targetPage in pagelist:
            print(targetPage)
            in_driver.get(targetPage)
            time.sleep(2)

            # find the div with name="reviews"
            review_div = in_driver.find_element(By.ID, "reviews")

            # inside that div, find the first <a> link
            link = review_div.find_element(By.TAG_NAME, "a")

            # get the link address (href)
            url = link.get_attribute("href")
            

            #get the last review page
            in_driver.get(url)
            time.sleep(2)
            countView = in_driver.find_element(By.CSS_SELECTOR, 'span[class^="PaginationContainer_paginationCount"]')
        #    countView = driver.find_element(By.CLASS_NAME, "PaginationContainer_paginationCount__DdbVG")
            count = countView.text.split(" ")[-2]
            count = int(count.replace(",",""))
            LastPageNum = math.ceil(count/10)
            print(count)
            print(LastPageNum)
            print(companyToSearch," complete")
            returnList.append((url,LastPageNum))
    finally:
        return returnList

driver = setupChrome()

input("Press Enter to Continue...")
driver.get("https://www.glassdoor.com/Reviews/index.htm")
input("Check login and cloudflare check. Press Enter to Continue...")

companies=[]

with open(".\Results\companylist.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    for row in rows[220:240]:
        #if row[0]==row[25]:
        #    companies.append("")
        #else:
            companies.append(row[0])
#companies = ["Google","Intel","IBM","Netflix","Amazon"]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

outfilename = f"output_{timestamp}.csv"
writer = csv.writer(open(outfilename, "w", newline="", encoding="utf-8"))
row = []
for company in companies:
    
    row.clear()
    row.append(company) 
#    for i in [1,2,3]:
    if company!="":
        resultList = findCompany(company,driver)
        for result in resultList:
            url = result[0]
            row.append(url)
            urlCompany = url.split(".htm")[0].split("/")[-1].replace("-"," ").split("Reviews")[0][:-1]
            page = result[1]
            row.append(page)
#    if urlCompany!=company:
#        row.append("Warning, Name not Match")
    writer.writerow(row)




