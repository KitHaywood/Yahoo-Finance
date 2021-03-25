import pandas as pd 
import yahoo_finance_api2 as yf 
from yahoo_finance_api2 import share
import requests
from yahoo_finance_api2 import exceptions
import datetime as dt 
import concurrent.futures

def get_ticker_dict():
    url = 'https://en.wikipedia.org/wiki/FTSE_100_Index#cite_note-13'
    html = requests.get(url).content
    df_list = pd.read_html(html)[3]
    tickerdict = [{'label':x['Company'],'value':x['EPIC']} for idx,x in df_list.iterrows()]
    return tickerdict

def get_ticker_data(ticker):
    my_share = share.Share(ticker)
    try:
        data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                        100,
                                                        share.FREQUENCY_TYPE_MINUTE,
                                                        30)                                               
        if data is not None:
            res = list(zip(data['timestamp'],data['open']))
            res = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in res]   
            df = pd.DataFrame.from_dict({
                'value':[x[1] for x in res],
                'time':[x[0] for x in res]
            })
            return df
        else:
            print('No Data from YahooFinance')     
            return None
    except exceptions.YahooFinanceError:
        pass      

# def get_good_tickers(tickerdict):
#     good_tickers = []
#     for x in get_ticker_dict():
#         for k,v in x.items():
#             if k=='label':
#                 pass
#             else:
#                 try:
#                     data = get_ticker_data(v)
#                     if data is not None:
#                         good_tickers.append(x)
#                     else:
#                         pass
#                 except exceptions.YahooFinanceError:
#                     pass    
#     return good_tickers                           

# def get_tick_data_dict(tickerdict):
#     good_tickers = []
#     data_dict = {}
#     for x in get_ticker_dict():
#         for k,v in x.items():
#             if k=='label':
#                 pass
#             else:
#                 try:
#                     data = get_ticker_data(v)
#                     if data is not None:
#                         good_tickers.append(x)
#                         data_dict[k]=data
#                     else:
#                         pass
#                 except exceptions.YahooFinanceError:
#                     pass    
#     return data_dict

if __name__=="__main__":
    tickerdict = get_ticker_dict()
    with concurrent.futures.ThreadPoolExecutor() as exec:
        results = {x['value']:exec.submit(get_ticker_data,x['value']) for x in tickerdict}
    results = {k:v.result() for k,v in results.items()}

    results = {k:v for k,v in results.items() if v is not None}

    print(results)


    # good_tick_dict = get_good_tickers(get_ticker_dict())
    # print(good_tick_dict)