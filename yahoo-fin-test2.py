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
import numpy as np 


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

def get_data():
    tickerdict = get_ticker_dict()
    with concurrent.futures.ThreadPoolExecutor() as exec:
        results = {x['value']:exec.submit(get_ticker_data,x['value']) for x in tickerdict}

    results = {k:v.result() for k,v in results.items()}
    results = {k:v for k,v in results.items() if v is not None}

    def make_good_ticker_dict(tickerdict,results):
        res = [x for x in tickerdict if x['value'] in results.keys()]
        return res

    good_ticker_dict = make_good_ticker_dict(tickerdict,results)
    return results


if __name__=="__main__":

    tickerdict = get_ticker_dict()
    with concurrent.futures.ThreadPoolExecutor() as exec:
        results = {x['value']:exec.submit(get_ticker_data,x['value']) for x in tickerdict}

    results = {k:v.result() for k,v in results.items()}
    results = {k:v.dropna() for k,v in results.items() if v is not None}

    def make_good_ticker_dict(tickerdict,results):
        res = [x for x in tickerdict if x['value'] in results.keys()]
        return res

    good_ticker_dict = make_good_ticker_dict(tickerdict,results)
    degree_options = [{'label':x,'value':x} for x in range(1,10)]

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(children='Test Yahoo Finance Fetcher',
        style={'textAlign':'center'}),
        html.H2('Select Stock'),
            dcc.Dropdown(
            id='ticker_dropdown',
            options=good_ticker_dict,
            value='AZN',
            style=dict(
                    width='40%',
                    verticalAlign="left")),
            html.H2('Select Polynomial Degree'),
            dcc.Dropdown(
                id='degrees',
                options=degree_options,
                value=4,
                style=dict(
                    width='40%',
                    verticalAlign="left")),
            html.Div([
                html.Div([
                    html.H3('Time Series'),
                    dcc.Graph(id='my_fig')],
                    className='six columns'),
                html.Div([
                    html.H3('Fitted Curve'),
                    dcc.Graph(id='my_fig2')],
                    className='six columns'),
                    ],className='row'),
            html.Div([
                html.Div([
                    html.H3('First Deriv'),
                    dcc.Graph(id='my_fig3')],
                    className='six columns'),
                html.Div([
                    html.H3('Second Deriv'),
                    dcc.Graph(id='my_fig4')],
                    className='six columns'),
                    ],className='row')
    ])

    @app.callback(
        [Output(component_id='my_fig', component_property='figure'),
        Output(component_id='my_fig2', component_property='figure'),
        Output(component_id='my_fig3', component_property='figure'),
        Output(component_id='my_fig4', component_property='figure')],
        [Input(component_id='ticker_dropdown', component_property='value'),
        Input(component_id='degrees',component_property='value')]
    )
    def update_line_chart(ticker,degree):
        good_data = results[ticker]
        try:
            fig1 = px.line(good_data,x='time',y='value')
            start = good_data['time'][0]
            time = np.array([pd.Timedelta(x-start).total_seconds() for x in good_data['time']])
            coefs = np.polyfit(time,np.array(good_data['value']),degree)
            print('coefs: ',coefs)
            coef_df = pd.DataFrame.from_dict({'time':time,
                                                'coeffs':np.polyval(coefs,time),
                                                'original_t':good_data['time']})
            fig2 = px.line(coef_df,x='original_t',y='coeffs')
            der1 = np.polyder(coefs,1)
            print('der1: ',der1)
            der1_df = pd.DataFrame.from_dict({'time':time,
                                                'der1':np.polyval(der1,time),
                                                'original_t':good_data['time']})
            fig3 = px.line(der1_df,x='original_t',y='der1')
            der2 = np.polyder(coefs,2)
            print('der2: ',der2) 
            der2_df = pd.DataFrame.from_dict({'time':time,
                                                'der2':np.polyval(der2,time),
                                                'original_t':good_data['time']})
            fig4 = px.line(der2_df,x='original_t',y='der2')
        except exceptions.YahooFinanceError:
            fig1 = 'No Ticker Available'
        return fig1, fig2, fig3, fig4

    app.run_server(debug=True)
