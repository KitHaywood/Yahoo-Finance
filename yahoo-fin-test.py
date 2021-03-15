import yahoo_finance as yf 
import requests
import pandas as pd 

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
        self.ticker = ticker


if __name__=="__main__":
    data = TickerTable().getTable()
    tickers = list(data['EPIC'])
    print(tickers)
    
    