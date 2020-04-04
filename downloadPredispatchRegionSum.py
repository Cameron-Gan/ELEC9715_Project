import requests
import re
import pandas as pd


def downloadPredispatchRegionSum():
    url = 'http://www.nemweb.com.au/REPORTS/CURRENT/PredispatchIS_Reports/'
    r = requests.get(url)
    r = r.text.split(sep="<br>")
    latest = r[len(r) - 2]
    latesturl = re.search(r'\"([^\"]*)\"', latest).group(1)

    zipfile = requests.get('http://www.nemweb.com.au'+latesturl)


if __name__ == "__main__":
    downloadPredispatchRegionSum()