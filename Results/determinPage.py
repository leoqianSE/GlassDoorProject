#this program visit each company's review page, based on the starting and ending dates
#identify the starting and ending page numbers 
#not complete, not being used

import csv
from gdtool import setupChrome, findPageOnDate
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from datetime import datetime
import math
import time
import json
import random



driver = setupChrome()

input("Press Enter to Continue...")
driver.get("https://www.glassdoor.com/Reviews/index.htm")
input("Check login and cloudflare check. Press Enter to Continue...")

color=[]
companies=[]
urls = []
startDate=[]
endDate=[]
totalPage=[]
startPage=[]
endPage=[]
foundstartpage=[]
foundendpage=[]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

outfilename = f"output_{timestamp}.csv"
writer = csv.writer(open(outfilename, "w", newline="", encoding="utf-8"))
writerow = []
with open(".\Results\DownloadListColored.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    for row in rows[80:100]:
        if row[0] not in ("green","duplicate") or int(row[12])<22:
            continue
        color.append(row[0])
        companies.append(row[8])
        urls.append(row[11])
        totalPage.append(row[12])
        startDate.append(row[13])
        endDate.append(row[14])
        sdate = datetime.strptime(row[13], "%m/%d/%Y")
        edate = datetime.strptime(row[14], "%m/%d/%Y")
        
        
        writerow.clear()
        writerow.append(row[8])
        writerow.append(row[12]) 
        writerow.append(findPageOnDate(driver, row[11],1,int(row[12]),sdate,"after"))
        writerow.append(findPageOnDate(driver, row[11],1,int(row[12]),edate,"before"))
        writer.writerow(writerow)



print(color,companies,urls,startDate,endDate,sdate,edate)


    