#this program visit each company's review page, based on the starting and ending dates
#identify the starting and ending page numbers 

import csv
from gdtool import setupChrome, toCSV, printandlog
from gdtool import findPageOnDate
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from datetime import datetime
import math
import time
import json
import random
from pathlib import Path
from bs4 import BeautifulSoup

def downloadpage(address,filename):
    driver.get(address)
    time.sleep(random.uniform(2,4))
    for i in range(10):  # scroll 10 times
        driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
        time.sleep(random.uniform(0.5, 1.5))  # simulate reading

    # Get the rendered HTML source
    html = driver.page_source
    
    
    # Choose output filename
    #filename = url.split("/")[-1]
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # Print the page title

    print(f"Saved page HTML to {filename}")
    return html



driver = setupChrome()

input("Press Enter to Continue...")
driver.get("https://www.glassdoor.com/Reviews/index.htm")
input("Check login and cloudflare check. Press Enter to Continue...")


#color=[]
#companies=[]
#urls = []
#startDate=[]
#endDate=[]
#totalPage=[]
#startPage=[]
#endPage=[]
#foundstartpage=[]
#foundendpage=[]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

outfilename = f"output_{timestamp}.csv"
recordcsv = Path(f"Results/{outfilename}")
writer = csv.writer(open(recordcsv, "w", newline="", encoding="utf-8"))
write_row = []

with open(".\Results\DownloadListColored.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    writer.writerow(["Company","Start From Page","#of Page Visited","#of Page Downloaded","#of Records Downloaded"])
    
    for row in rows[194:]:
        write_row.clear()
        if row[0] not in ("green","duplicate"):
            print(f"Skip {row[8]}")
            write_row.append(row[8])
            writer.writerow(write_row)
            continue
        sdate = datetime.strptime(row[13], "%m/%d/%Y")
        edate = datetime.strptime(row[14], "%m/%d/%Y")
        originalUrl = row[11]

        firstpage=-1
        #

        #find the first page to start
        if int(row[12])>7:
            firstpage = findPageOnDate(driver, row[11],1,int(row[12]),edate,"before")
            firstpage-=1 #add some buffer by starting one page before
        else:
            firstpage=1
        
        #firstpage=457
        write_row.append(row[8])
        write_row.append(firstpage)

        #go to first page and start download till hit the end or hit the sdate
        urlpre = originalUrl.split(".htm")[0]
        urlmid = "_P"
        urlpost= ".htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME"
        company = urlpre.split("/")[-1].replace("-"," ").split("Reviews")[0][:-1]
        folder = Path(f"Results/{row[8]}")
        folder.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"log_{company}_{timestamp}.txt"
        log_path=folder/log_file
        printandlog(log_path,f"Start from page {firstpage}")
        
        i = firstpage
        pagecount = 0
        recordtotal = 0
        visitedPage = 0
        while True: #for one page i
#    path = os.path.join(folder,urlpre.split("/")[-1]+urlmid+i+".html")
            if i==-1:
                break
            path = folder/(urlpre.split("/")[-1]+urlmid+str(i)+".html")
            redownloaded = False
            while(True):
                html = downloadpage(urlpre+urlmid+str(i)+urlpost,path)
                printandlog(log_path,f"Saved page HTML to {path}")
                #check if the file is good
                soup = BeautifulSoup(html, "html.parser")
                
                # Find the script tag
                script_tag = soup.find("script", id="__NEXT_DATA__")
                if script_tag is not None:
                    data = json.loads(script_tag.string)
                    recordcount = [0]
                    newrows = toCSV(data["props"]["pageProps"]["apolloCache"],recordcount)
                    datelist = []
                    for a in newrows:
                        currentrow = list(a)
                        #print(currentrow[6])
                        datelist.append(datetime.strptime(currentrow[6], "%Y-%m-%d"))
                    printandlog(log_path,f"found {len(datelist)} records")
                    visitedPage+=1

                    if len(datelist)<1:
                        printandlog(log_path,f"current page {i} is not needed, delete it")
                        if path.exists():
                               path.unlink()
                               printandlog(log_path,f"{path} File deleted")
                        else:
                           printandlog(log_path,f"{path}File not found")
                        printandlog(log_path,f"Reach the end of all reviews at page {i}")
                        i=-1
                        break
                    mindate=datelist[-1]
                    maxdate=datelist[0]
                    recordNum = len(newrows)

                    if mindate>edate: #no need for this page and move on one page
                        printandlog(log_path,f"current page {i} is not needed, delete it")
                        if path.exists():
                               path.unlink()
                               printandlog(log_path,f"{path} File deleted")
                        else:
                           printandlog(log_path,f"{path}File not found")
                        if recordNum<10:
                            printandlog(log_path,f"Reach the end of all reviews at page {i}")
                            i = -1
                        else:
                            i+=1
                        break
                    elif maxdate<sdate: #went too far, no need for any page on this company
                        printandlog(log_path,f"current page {i} is not needed, delete it")
                        printandlog(log_path,f"Hit the end, no more page needed after page {i}")
                        
                        i=-1
                        break
                    else:# maxdate>=edate: #need download this page
                        
                        printandlog(log_path,f"{recordNum} entries are found")
                        recordtotal+=recordNum
                        pagecount+=1
                        
                        if recordNum<10:
                            printandlog(log_path,f"Reach the end of all reviews at page {i}")
                            i = -1
                        else:
                            i+=1
                        break
                    #else:
                    #    print(f"Hit the end, no more page needed after page {i}")
                    #    i=-1
                    #    break
                else: #what if the tag is none
                    printandlog(log_path,f"need Redownload page {i}")

        write_row.append(visitedPage)
        write_row.append(pagecount)
        write_row.append(recordtotal)
        
        writer.writerow(write_row)
                        
                
                
                
                


        #color.append(row[0])
        #companies.append(row[8])
        #urls.append(row[11])
        #totalPage.append(row[12])
        #startDate.append(row[13])
        #endDate.append(row[14])
        
        
        
        #writerow.clear()
        #writerow.append(row[8])
        #writerow.append(row[12]) 
        #writerow.append(findPageOnDate(driver, row[11],1,int(row[12]),sdate,"after"))
        #writerow.append(findPageOnDate(driver, row[11],1,int(row[12]),edate,"before"))
        #writer.writerow(writerow)






    