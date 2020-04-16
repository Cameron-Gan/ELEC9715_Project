import io
import re
import zipfile
from abc import ABC, abstractmethod
import requests
import pandas as pd


class PackageInterface(ABC):

    def __init__(self):
        self.raw_data = None
        pass

    @abstractmethod
    def get_raw_data(self):
        pass

    @abstractmethod
    def get_table(self, string):
        pass

    def refresh_raw_data(self):
        self.raw_data = self.get_raw_data()


class Predispatch(PackageInterface):
    url = 'http://www.nemweb.com.au/REPORTS/CURRENT/PredispatchIS_Reports/'

    tables = {}

    def __init__(self):
        super().__init__()
        self.raw_data = self.get_raw_data()

    def get_raw_data(self):
        r = requests.get(self.url)
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


class Dispatch(PackageInterface):
    def get_table(self, string):
        pass

    def get_raw_data(self):
        pass

    tables = ["list", "of", "things"]

# if __name__ == '__main__':
#     predispatch = Predispatch()
#     region_solution = predispatch.get_table(table_string='REGION_SOLUTION')
#     print(region_solution.shape)
