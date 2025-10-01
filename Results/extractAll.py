import csv
from gdtool import toCSV, printandlog
from datetime import datetime
import json,gc
from pathlib import Path
from bs4 import BeautifulSoup

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

outfilename = f"output_{timestamp}.csv"
recordcsv = Path(f"Results/{outfilename}")
writer = csv.writer(open(recordcsv, "w", newline="", encoding="utf-8"))
write_row = []
totalfileprocessed = 0
failprocessed=0
successprocessed=0
recordcount=[0]

log_file = f"log_{timestamp}.txt"
log_path=Path(f"Results/{log_file}")
with open(".\Results\DownloadListColored.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    #writer.writerow(["Company","Start From Page","#of Page Visited","#of Page Downloaded","#of Records Downloaded"])
    
    for row in rows[100:]:
        write_row.clear()
        company = row[18]
        numofPage = 0 if row[21]=="" else int(row[21])
        numofRecord = 0 if row[22]=="" else int(row[22])
        sdate = datetime.strptime(row[13], "%m/%d/%Y")
        edate = datetime.strptime(row[14], "%m/%d/%Y")
        
        if numofPage<1:
            printandlog(log_path,f"No record to collect, skip {company}")
            continue
        
        printandlog(log_path,f"\n\nExtracting from {company}, there are {numofPage} pages, {numofRecord} reviews")
        folder = Path(f"Results\{company}")
        if not folder.exists():
            printandlog(log_path,f"Something is wrong, {folder} doesn't exist")
            continue
        numofPageoneCompany=0
        numofRecordoneCompany=0
        for file_path in folder.glob("*.htm*"):  # only .html or htm files
            totalfileprocessed+=1
            numofPageoneCompany+=1
            printandlog(log_path,f"Processing: {file_path.name}\n")
            try:
             #   if not file_path.name.startswith("Intel"):
                #   continue
                with open(f"{folder}\\{file_path.name}", encoding="utf-8") as f:
                    html = f.read()
                    # Parse HTML
                    soup = BeautifulSoup(html, "html.parser")

                    # Find the script tag
                    script_tag = soup.find("script", id="__NEXT_DATA__")
                    del soup
                    gc.collect()
        
                    # Extract and parse JSON
                    data = json.loads(script_tag.string)
                    newrows = toCSV(data["props"]["pageProps"]["apolloCache"],recordcount)
                    #writer.writerows(newrows)
                    newrows = list(newrows)
                    temprows = []
                    for individualRow in newrows:
                        individualRow.append(sdate.date())
                        individualRow.append(edate.date())
                        temprows.append(individualRow)
                        numofRecordoneCompany+=1
                    writer.writerows(temprows)
                    printandlog(log_path,f"Processing: {file_path.name} Successful")
                    successprocessed+=1
            except Exception as e:
                printandlog(log_path,f"ERROR in {file_path.name}: {e}")
                failprocessed+=1
                continue
        if numofRecordoneCompany==numofRecord and numofPage==numofPageoneCompany:
            printandlog(log_path,f"number of page and record checked correct for {company}")
        else:
            printandlog(log_path,f"Error number of page and records not match for {company}, could be 2 spinoff")
            printandlog(log_path,f"Number of processed page is {numofPageoneCompany}, Number of processed Record is {numofRecordoneCompany}")

printandlog(log_path,f"Total processed: {totalfileprocessed}")
printandlog(log_path,f"Total Success processed: {successprocessed}")
printandlog(log_path,f"Total Fail processed: {failprocessed}")
printandlog(log_path,f"Total Records Added: {recordcount[0]}")
        