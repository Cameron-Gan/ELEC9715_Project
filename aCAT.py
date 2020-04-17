import io
import re
import zipfile
from abc import ABC, abstractmethod
import requests
import pandas as pd
from datetime import datetime, timedelta
from helperFunctions import floor_ft

class PackageInterface(ABC):

    url = None

    def __init__(self):
        self.raw_data = None


    @abstractmethod
    def get_table(self, string):
        pass

    def refresh_raw_data(self):
        self.raw_data = self.get_raw_data()

    def geturl(self):
        return self.url

    @abstractmethod
    def get_raw_data(self):
        pass


class Predispatch(PackageInterface):

    tables = {}

    def __init__(self):
        super().__init__()
        self.url = 'http://nemweb.com.au/Reports/Current/PredispatchIS_Reports/'
        self.raw_data = self.get_raw_data()

    def get_raw_data(self):
        r = requests.get(self.geturl())

        r = r.text.split(sep="<br>")
        latest = r[len(r) - 2]
        most_recent = re.search(r'\"([^\"]*)\"', latest).group(1)
        most_recent_url = 'http://www.nemweb.com.au' + most_recent

        r1 = requests.get(most_recent_url)
        return io.BytesIO(r1.content)

    def get_table(self, table_string):
        df_list = []
        _zip = zipfile.ZipFile(self.raw_data)
        with _zip.open(_zip.infolist()[0]) as fp:
            for line in fp.readlines():
                if re.search(table_string, str(line)):
                    columns = re.split(',', str(line.strip()))
                    df_list.append(columns)
        return pd.DataFrame(df_list[1:], columns=df_list[0])


def scrap_tables(raw_data):
    region_sum = []
    price = []
    _zip = zipfile.ZipFile(io.BytesIO(raw_data))
    with _zip.open(_zip.infolist()[0]) as fp:
        for line in fp.readlines():
            if re.search("REGIONSUM", str(line)):
                columns = re.split(',', str(line.strip()))
                region_sum.append(columns)
            if re.search("TRADING,PRICE", str(line)):
                columns = re.split(',', str(line.strip()))
                price.append(columns)

    return region_sum, price


class Dispatch(PackageInterface):

    def __init__(self):
        super().__init__()
        self.url = 'http://nemweb.com.au/Reports/Current/TradingIS_Reports/'
        self.region_sum_df, self.price_df = self.get_raw_data()

    def get_raw_data(self):
        current_time = datetime.now()
        current_time_floored = floor_ft(current_time, timedelta(minutes=30))
        search_time = current_time_floored - timedelta(minutes=5)
        previous_24hrs = search_time - timedelta(hours=24)
        previous_24hrs_string = f'{previous_24hrs:%A},{previous_24hrs:%B}{previous_24hrs.day},{previous_24hrs:%Y}{previous_24hrs.month}:{previous_24hrs.minute}{previous_24hrs:%p}'

        print(previous_24hrs_string)

        raw_text = requests.get(self.geturl())
        raw_text = raw_text.text.split(sep='<br>')
        index_of_start = 0
        for index, line in enumerate(raw_text):
            # print(line)
            if re.search(previous_24hrs_string, re.sub('\s*', '', line)):
                print(line)
                index_of_start = index
                break

        region_sum_list = []
        price_list = []

        for x in range(index_of_start, (len(raw_text) - 1)):
            # print(raw_text[x])
            zip_file_name = re.search(r'\"([^\"]*)\"', raw_text[x]).group(1)
            # print('http://nemweb.com.au' + zip_file_name)
            table_data = requests.get('http://nemweb.com.au' + zip_file_name)
            region_sum, price = scrap_tables(table_data.content)
            region_sum_list = region_sum_list + region_sum
            price_list = price_list + price

        region_sum_df = pd.DataFrame(region_sum_list[1:], columns=region_sum_list[0])
        region_sum_df = region_sum_df[region_sum_df['b\'I'] != 'b\'I']
        price_df = pd.DataFrame(price_list[1:], columns=price_list[0])
        price_df = price_df[price_df['b\'I'] != 'b\'I']

        return region_sum_df, price_df

    def get_table(self, string):
        if string == "REGION_SOLUTION":
            return self.region_sum_df
        if string == "REGION_PRICE":
            return self.price_df
        else:
            return "not a valid string"


if __name__ == '__main__':
    dispatch = Dispatch()
    pass


