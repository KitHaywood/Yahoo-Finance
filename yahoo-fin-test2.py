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
    with concurrent.futures.ThreadPoolExecutor() as exec:
        results = {x['value']:exec.submit(get_ticker_data,x['value']) for x in tickerdict}

    results = {k:v.result() for k,v in results.items()}
    results = {k:v for k,v in results.items() if v is not None}

    def make_good_ticker_dict(tickerdict,results):
        res = [x for x in tickerdict if x['value'] in results.keys()]
        return res

    good_ticker_dict = make_good_ticker_dict(tickerdict,results)
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
                html.H1(children='Test Yahoo Finance Fetcher',
                style={'textAlign':'center'}),
                    dcc.Dropdown(
                    id='ticker_dropdown',
                    options=good_ticker_dict,
                    value='AZN'),
                dcc.Graph(id='my_fig')]
                )
    @app.callback(
        Output(component_id='my_fig', component_property='figure'),
        [Input(component_id='ticker_dropdown', component_property='value')]
    )
    def update_line_chart(ticker):
        good_data = results[ticker]
        try:
            fig = px.line(good_data,x='time',y='value')
        except exceptions.YahooFinanceError:
            fig = 'No Ticker Available'
        return fig
    app.run_server(debug=True)
