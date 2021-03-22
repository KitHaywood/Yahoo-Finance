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


def update_line_chart(ticker):
    print(ticker)
    data = GetTickerData().get_data(ticker)
    data_df = pd.DataFrame.from_dict({
        'value':[x[1] for x in data],
        'time':[x[0] for x in dat]
        })
    fig = px.line(data_df,x='time',y='value')
    fig.update_layout(transition_duration=500)
    return fig

class Tickers(object):
    def __init__(self):
        super().__init__()
        self.url = 'https://en.wikipedia.org/wiki/FTSE_100_Index#cite_note-13'
        self.html = requests.get(self.url).content
        self.df_list = pd.read_html(self.html)[3]
    
    def getTable(self):
        return self.df_list
    
    def getDict(self):
        tickerdict = [{'label':x['Company'],'value':x['EPIC']} for idx,x in self.df_list.iterrows()]
        return tickerdict

class GetTickerData():
    def __init__(self):
        self.ticker_table = Tickers().getTable()
        self.tickerdict = Tickers().getDict()
    def get_data(self,ticker):
        self.ticker = ticker
        if isinstance(self.ticker,str):
            print('took_str_option')
            self.my_share = share.Share(self.ticker)
            self.data = self.my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                    100,
                                                    share.FREQUENCY_TYPE_MINUTE,
                                                    30)
            self.result = list(zip(self.data['timestamp'],self.data['open']))
            self.result = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in self.result]  
            return self.result

        elif isinstance(self.ticker,list):
            print('took_list_option')
            self.my_share = share.Share(self.ticker)
            self.data = self.my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                    1000,
                                                    share.FREQUENCY_TYPE_MINUTE,
                                                    50)
            self.result = list(zip(self.data['timestamp'],self.data['open']))
            self.result = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in self.result]
            return self.result
        
class App():
    def __init__(self):
        super().__init__()
        self.ticker_table = Tickers().getTable()
        self.tickerdict = Tickers().getDict()
        self.ticker = 'AAL'
        self.result = GetTickerData().get_data(self.ticker)
        my_df = pd.DataFrame.from_dict({
        'value':[x[1] for x in self.result],
        'time':[x[0] for x in self.result]
        })
        my_fig = px.line(my_df,x='time',y='value')
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div(children=[
            html.H1(children='Test Yahoo Finance Fetcher',
            style={'textAlign':'center'}),
                dcc.Dropdown(
                id='ticker_dropdown',
                options=self.tickerdict,
                value='AAL'),
            dcc.Graph(id='my_fig',figure=my_fig)])
        self.app.run_server(debug=True)

if __name__=="__main__":
    app = dash.Dash(__name__)
    @app.callback(
    Output(component_id='my_fig', component_property='figure'),
    [Input(component_id='ticker_dropdown', component_property='value')]
    )
    App()
