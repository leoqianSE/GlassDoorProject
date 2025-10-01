#resources used to extract review data from html file from glassdoor
#import this file in extract program

from pathlib import Path
#from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from datetime import datetime
import time, random, json
from bs4 import BeautifulSoup

columns=[["Review ID", "reviewId"],["Employer","employer","shortName"],["Job Title","jobTitle","text"],["Location","location","name"],["Employment Status","employmentStatus"],["Length of Employment","lengthOfEmployment"],
         ["Review Date","reviewDateTime"],["Review Time","reviewDateTime"],["Is Current Job","isCurrentJob"],["Overall Rating","ratingOverall"],["WorkLifeBalance Rating","ratingWorkLifeBalance"],["CultureAndValues Rating","ratingCultureAndValues"],
         ["DiversityAndInclusion Rating","ratingDiversityAndInclusion"],["CareerOpportunities Rating","ratingCareerOpportunities"],
         ["CompensationAndBenefits Rating","ratingCompensationAndBenefits"],["SeniorLeadership Rating","ratingSeniorLeadership"],
         ["BusinessOutlook Rating","ratingBusinessOutlook"],["RecommendToFriend Rating","ratingRecommendToFriend"],["CEO Rating","ratingCeo"],
         ["Summary","summary"],["Pros","pros"],["Cons","cons"],["Advice","advice"],["Summary Original","summaryOriginal"],["Pros Original","prosOriginal"],["Cons Original","consOriginal"],["Advice Original","adviceOriginal"],["Count Helpful","countHelpful"],
         ["Count Not Helpful","countNotHelpful"],["Translation Method","translationMethod"]]
# Path to your ChromeDriver
CHROMEDRIVER_PATH = r".\chromedriver140\chromedriver.exe"

# Path to the Chrome browser you want to use
CHROME_BINARY_PATH = r".\chrome-win64\chrome.exe"

# (Optional) Path to your Chrome user data and profile name
USE_PROFILE = True   # change to True if you want to use your real profile
USER_DATA_DIR = r"C:\Users\lqian\Desktop\Working on\UserProfiles"
USER_DATA_DIR2 = r"C:\Users\leo_q\Desktop\Working on\UserProfiles"
PROFILE_NAME = "Profile 1"  # could be "Profile 1", "Profile 2", etc.

# Run headless (no visible browser window)
HEADLESS = False

def printandlog(logfile_path,str):
    print(str)
    with open(logfile_path, "a", encoding="utf-8") as f:
        f.write(str+"\n")

def toCSV(node,count=[0]):
    # List to hold all CSV rows
    csv_rows = []
    
    # Temporary list for current row
    current_row = []
        
    for k, v in node.items():
        if(k.startswith("EmployerReviewRG:")):
            current_row = []
            for i in columns:
                if(isinstance(v[i[1]],dict)):
                    current_row.append(node[v[i[1]]["__ref"]][i[2]])
                else:
                    if i[0]=="Review Date":
                        current_row.append(v[i[1]].split("T")[0])
                    elif i[0]=="Review Time":
                        current_row.append(v[i[1]].split("T")[1])
                    else:
                        current_row.append(v[i[1]])
            csv_rows.append(current_row)
            count[0]+=1
    print(f"In this file {count[0]} record added")
    return csv_rows

def setupChrome():
    # Update this path to where you saved chromedriver.exe
    myservice = Service(CHROMEDRIVER_PATH)

    # Path to the Chrome browser you want to use
    options = Options()
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument("--log-level=3")  # suppress Chrome noise
    options.add_argument("--no-first-run")                        # skip first run tab
    options.add_argument("--no-default-browser-check")  

    if USE_PROFILE:
        p = Path(USER_DATA_DIR)
        if p.exists():
            options.add_argument(f"user-data-dir={USER_DATA_DIR}")
            print(USER_DATA_DIR)
        elif Path(USER_DATA_DIR2).exists():
            options.add_argument(f"user-data-dir={USER_DATA_DIR2}")
            print(USER_DATA_DIR2)
        else:
            print("Please type profile path")
            DIR = input("Please type profile path")
            options.add_argument(f"user-data-dir={DIR}")
        
        options.add_argument(f"profile-directory={PROFILE_NAME}")

    if HEADLESS:
        options.add_argument("--headless")
        
    # Create browser window
    #driver = webdriver.Chrome(service=myservice)
    driver = uc.Chrome(service=myservice, options=options)

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[0])
        driver.close()                 # close unwanted tab
        driver.switch_to.window(driver.window_handles[0])
    
    return driver

def findPageOnDate(driver, url,startfrom,endat,dateTarget,beforeOrAfter):
    originalUrl = url
    firstpage = startfrom
    lastpage = endat
    urlpre = originalUrl.split(".htm")[0]
    urlmid = "_P"
    urlpost= ".htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME"
    
    found = False
    recordcount=[0]


    midpage=1
    while firstpage<=lastpage and not found:
        midpage = (firstpage+lastpage)//2
        address = urlpre+urlmid+f"{midpage}"+urlpost
        while True:
            driver.get(address)
            time.sleep(random.uniform(2,7))
            html = driver.page_source
            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Find the script tag
            script_tag = soup.find("script", id="__NEXT_DATA__")
            if script_tag is not None:
                break
            else:
                print("Reloading, need pass human checker")
            
        # Extract and parse JSON
        data = json.loads(script_tag.string)
        newrows = toCSV(data["props"]["pageProps"]["apolloCache"],recordcount)
        datelist = []
        for a in newrows:
            currentrow = list(a)
            #print(currentrow[6])
            datelist.append(datetime.strptime(currentrow[6], "%Y-%m-%d"))
        mindate=datelist[-1]
        maxdate=datelist[0]
        print(f"checking {midpage}")
        if dateTarget>maxdate:
            lastpage = midpage-1
        elif dateTarget<mindate:
            firstpage=midpage+1
        elif dateTarget<maxdate and dateTarget>mindate:
            found = True
        elif maxdate>mindate and dateTarget==mindate and beforeOrAfter=="before":
            firstpage = midpage+1
        elif maxdate>mindate and dateTarget==maxdate and beforeOrAfter=="before":
            found=True
        elif maxdate>mindate and dateTarget==mindate and beforeOrAfter=="after":
            found = True
        elif maxdate>mindate and dateTarget==maxdate and beforeOrAfter=="after":
            lastpage = midpage-1
        elif maxdate==mindate and dateTarget==maxdate and beforeOrAfter=="before":
            firstpage = midpage+1
        elif maxdate==mindate and dateTarget==maxdate and beforeOrAfter=="after":
            lastpage = midpage-1
    if found is True:
        print(midpage)
        
    elif beforeOrAfter=="before":
        midpage=firstpage-1
        print(midpage)
        
    else:
        midpage=lastpage+1
        print(midpage)
    
    return midpage


#__all__=["BeautifulSoup","json","csv","datetime","Path","columns","toCSV"]