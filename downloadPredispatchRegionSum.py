import requests
import re

def downloadPredispatchRegionSum():
    url = 'http://www.nemweb.com.au/REPORTS/CURRENT/PredispatchIS_Reports/'
    r = requests.get(url)
    r = r.text.split(sep="<br>")
    latest = r[len(r) - 2]
    print(latest)
    latesturl = re.search(r'\"[^\"]*\"', latest)
    print(latesturl(1))
    

if __name__ == "__main__":
    downloadPredispatchRegionSum()