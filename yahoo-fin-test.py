import yahoo_finance_api2 as yf 
from yahoo_finance_api2 import share
import requests
import pandas as pd 
import datetime as dt 

class TickerTable():
    def __init__(self):
        super().__init__()
    
    def getTable(self):
        self.url = 'https://en.wikipedia.org/wiki/FTSE_100_Index#cite_note-13'
        self.html = requests.get(self.url).content
        self.df_list = pd.read_html(self.html)[3]
        return self.df_list
    
class getTickerData():
    def __init__(self):
        super().__init__()

    def getData(self,ticker):
        self.share = share.Share(ticker)
        self.data = self.share.get_historical(share.PERIOD_TYPE_DAY,
                                                365,
                                                share.FREQUENCY_TYPE_MINUTE,
                                                5)
        return self.data



if __name__=="__main__":
    data = TickerTable().getTable()
    tickers = list(data['EPIC'])
    test_ts = getTickerData().getData('AAL')
    print(test_ts.keys())
    
    