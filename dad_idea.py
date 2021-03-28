import yahoo_finance_api2 as yf 
from yahoo_finance_api2 import share
import requests
import pandas as pd 
import datetime as dt 
import dash
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.express as px 
from dash.dependencies import Input, Output
from yahoo_finance_api2 import exceptions
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

if __name__=="__main__":

    tickerdict = get_ticker_dict()
    print(tickerdict)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = {x['value']:executor.submit(get_ticker_data,x['value']) for x in tickerdict}

    results = {k:v.result() for k,v in results.items()}
    results = {k:v for k,v in results.items() if v is not None}
    results = {k:v.dropna() for k,v in results.items()}

    def make_good_ticker_dict(tickerdict,results):
        res = [x for x in tickerdict if x['value'] in results.keys()]
        return res

    good_ticker_dict = make_good_ticker_dict(tickerdict,results)
    print(results['WPP'])
    
    def get_pc_return(df):
        start = df.loc[0,'value']
        df['ma_10'] = df['value'].rolling(window=10).mean()
        df['10_day_pcr'] = [x/start for x in df['value']]
        df = df.fillna(0)
        return df
    

    def get_ma_pcr(df):

        return None

    pc_return_dict = {k:get_pc_return(v) for k,v in results.items()}
    print(pc_return_dict['WPP'])
    def buy_stock(df):
        # df['buy'] = ['buy' if ((df['value'].loc[x]-df['value'].loc[x-10])/df['value'].loc[x]>0.05) else None for x in range(10,len(df['value']-1))]
        for i,v in df.iterrows():
            if i<10:
                v['buy'] = 0
            else:
                if (v['value']-df['value'].loc[i]/v['value'])>0.05:
                    v['buy'] = 'buy'
                else:
                    pass
        return df

    pcr10 = {k:buy_stock(v) for k,v in results.items()}
    print(pcr10)

    # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    # app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    # app.layout = html.Div(children=[
    #             html.H1(children='Test Yahoo Finance Fetcher',
    #             style={'textAlign':'center'}),
    #                 dcc.Dropdown(
    #                 id='ticker_dropdown',
    #                 options=good_ticker_dict,
    #                 value='AZN'),
    #             dcc.Graph(id='my_fig')]
    #             )
    # @app.callback(
    #     Output(component_id='my_fig', component_property='figure'),
    #     [Input(component_id='ticker_dropdown', component_property='value')]
    # )
    # def update_line_chart(ticker):
    #     good_data = results[ticker]
    #     try:
    #         fig = px.line(good_data,x='time',y='value')
    #     except exceptions.YahooFinanceError:
    #         fig = 'No Ticker Available'
    #     return fig
    # app.run_server(debug=True)
