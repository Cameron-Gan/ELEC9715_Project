import io
import shutil
from matplotlib import pyplot as plt
import requests
import re
import os
import pandas as pd
import zipfile


def downloadPredispatchRegionSum():
    url = 'http://www.nemweb.com.au/REPORTS/CURRENT/PredispatchIS_Reports/'
    r = requests.get(url)
    r = r.text.split(sep="<br>")
    latest = r[len(r) - 2]
    latestfilepath = re.search(r'\"([^\"]*)\"', latest).group(1)
    filename = latestfilepath.split("/")[4]
    filename = filename.split(".")[0] + ".csv"
    print(filename)
    latesturl = 'http://www.nemweb.com.au' + latestfilepath
    print(latesturl)

    r1 = requests.get(latesturl)

    z = zipfile.ZipFile(io.BytesIO(r1.content))
    regionSolutionList = []
    regionPriceList = []
    with z.open(z.namelist()[0]) as fp:
        i = 0
        for line in fp.readlines():
            if re.search('REGION_SOLUTION,', str(line)):
                columns = re.split(',', str(line.strip()))
                regionSolutionList.append(columns)
            if re.search('REGION_PRICE', str(line)):
                columns = re.split(',', str(line.strip()))
                regionPriceList.append(columns)
            if re.search('I,PREDISPATCH,INTERCONNECTOR_SOLN', str(line)):
                break

    regionSolutionDF = pd.DataFrame(regionSolutionList[1:], columns=regionSolutionList[0])
    regionPriceDF = pd.DataFrame(regionPriceList[1:], columns=regionPriceList[0])

    print(type(regionSolutionDF.CLEAREDSUPPLY[0]))

    fig, ax1 = plt.subplots()

    color1 = 'tab:red'
    ax1.set_ylabel('predicted demand', color=color1)
    ax1.plot(regionSolutionDF[regionSolutionDF.REGIONID == "NSW1"].PERIODID.astype(int),
                regionSolutionDF[regionSolutionDF.REGIONID == "NSW1"].CLEAREDSUPPLY.astype(float), color=color1)
    ax2 = ax1.twinx()

    color2 = 'tab:blue'
    ax2.set_ylabel('predicted price', color=color2)
    ax2.plot(regionSolutionDF[regionSolutionDF.REGIONID == "NSW1"].PERIODID.astype(int),
             regionPriceDF[regionPriceDF.REGIONID == "NSW1"].RRP.astype(float))

    fig.tight_layout()
    plt.show()

    # plt.plot(regionSolutionDF[regionSolutionDF.REGIONID == "NSW1"].PERIODID.astype(int),
    #             regionSolutionDF[regionSolutionDF.REGIONID == "NSW1"].CLEAREDSUPPLY.astype(float))
    # plt.show()
    print(regionSolutionDF[regionPriceDF.REGIONID == 'NSW1'].CLEAREDSUPPLY)

if __name__ == "__main__":
    downloadPredispatchRegionSum()
