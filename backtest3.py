import yahoo_finance_api2 as yf 
from yahoo_finance_api2 import share
import requests
import pandas as pd 
import datetime as dt 
import dash
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.express as px 
from plotly.graph_objects import Scatter
from dash.dependencies import Input, Output
from yahoo_finance_api2 import exceptions
import concurrent.futures
import multiprocessing as mp
import numpy as np
from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover


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

def get_ticker_data_1(ticker):
    my_share = share.Share(ticker)
    try:
        data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                        100,
                                                        share.FREQUENCY_TYPE_MINUTE,
                                                        30)                                               
        if data is not None:
            res = list(zip(data['timestamp'],data['open'],data['high'],data['low'],data['close']))
            res = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in res]   
            df = pd.DataFrame(res,columns=['time','open','high','low','close'])
            print(df.columns)
            return df
        else:
            print('No Data from YahooFinance')     
            return None
    except exceptions.YahooFinanceError:
        pass

def get_ticker_data_2(ticker):
    my_share = share.Share(ticker)
    try:
        data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                        100,
                                                        share.FREQUENCY_TYPE_MINUTE,
                                                        30)                                               
        if data is not None:
            df = pd.DataFrame.from_dict(data)
            df['timestamp'] = [dt.datetime.fromtimestamp(x/1000) for x in df['timestamp']]
            df = df.set_index('timestamp')
            df.columns = ['Open','High','Low','Close','Volume']
            df = df.interpolate()
            return df
        else:
            print('No Data from YahooFinance')     
            return None
    except exceptions.YahooFinanceError:
        pass

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


if __name__=="__main__":
    mp.set_start_method('fork')
    tickerdict = get_ticker_dict()
    # with concurrent.futures.ThreadPoolExecutor() as exec:
    #     results = {x['value']:exec.submit(get_ticker_data_2,x['value']) for x in tickerdict}

    # results = {k:v.result() for k,v in results.items()}
    # results = {k:v.dropna() for k,v in results.items() if v is not None}

    # def make_good_ticker_dict(tickerdict,results):
    #     res = [x for x in tickerdict if x['value'] in results.keys()]
    #     return res

    # good_ticker_dict = make_good_ticker_dict(tickerdict,results)

    # degree_options = [{'label':x,'value':x} for x in range(1,10)]

    result = {}
    result['WPP'] = get_ticker_data_2('WPP')
    bt = Backtest(result['WPP'], SmaCross, cash=10_000, commission=.002)
    stats = bt.optimize(n1=range(5, 50, 5),
            n2=range(10, 200, 5),
            maximize='Equity Final [$]',
            constraint=lambda param: param.n1 < param.n2)
    eq_curve = stats._equity_curve
    eq_curve['time'] = eq_curve.index
    fig5 = px.line(eq_curve,x='time',y='Equity',template='simple_white')
    print(stats._strategy.n1)
    print(stats._strategy.n2)


    # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    # app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    # app.layout = html.Div(children=[
    #     html.H1(children='Test Yahoo Finance Fetcher',
    #     style={'textAlign':'center'}),
    #     html.Div(className='row',children=[
    #         html.Div(className='four columns', children=[
    #             html.Label(['Select Stock'],style={'text-align':'center'}),
    #             dcc.Dropdown(
    #             id='ticker_dropdown',
    #             options=good_ticker_dict,
    #             value='AZN'), 
    #         ]),
    #         html.Div(className='four columns', children=[
    #             html.Label(['Select Degree'],style={'text-align':'center'}),
    #             dcc.Dropdown(
    #             id='degrees',
    #             options=degree_options,
    #             value=4), 
    #         ]),
    #     ],style=dict(display='flex')),
    #         html.Div([
    #             html.Div([
    #                 dcc.Graph(id='my_fig')],
    #                 className='six columns'),
    #             html.Div([
    #                 dcc.Graph(id='my_fig2')],
    #                 className='six columns'),
    #                 ],className='row'),
    #         html.Div([
    #             html.Div([
    #                 dcc.Graph(id='my_fig3')],
    #                 className='six columns'),
    #             html.Div([
    #                 dcc.Graph(id='my_fig4')],
    #                 className='six columns'),
    #                 ],className='row'),
    #             html.Div([html.H3(['SMA Cross'])]),
    #             dcc.Graph(id='my_fig5'),
    #             html.H5('Line Fit Co-Efficients'),
    #             html.P(id='coefs'),
    #             html.H5('SMA Cross Optimal'),
    #             html.P(id='smac')
    # ])
    # @app.callback(
    #     [Output(component_id='my_fig', component_property='figure'),
    #     Output(component_id='my_fig2', component_property='figure'),
    #     Output(component_id='my_fig3', component_property='figure'),
    #     Output(component_id='my_fig4', component_property='figure'),
    #     Output(component_id='my_fig5', component_property='figure'),
    #     Output(component_id='coefs',component_property='children'),
    #     Output(component_id='smac',component_property='children')],
    #     [Input(component_id='ticker_dropdown', component_property='value'),
    #     Input(component_id='degrees',component_property='value')]
    # )
    # def update_line_chart(ticker,degree):
    #     good_data = results[ticker]
    #     try:
    #         good_data['time'] = good_data.index  
    #         fig1 = px.scatter(good_data,x='time',y='Open',template='simple_white',title='Time Series')
    #         fig1.update_traces(marker={'size': 4})
                      
    #         start = good_data['time'][0]
    #         time = np.array([pd.Timedelta(x-start).total_seconds() for x in good_data['time']])
    #         coefs = np.polyfit(time,np.array(good_data['Open']),degree)
    #         print('coefs: ',coefs)
    #         coef_df = pd.DataFrame.from_dict({'time':time,
    #                                             'coeffs':np.polyval(coefs,time),
    #                                             'original_t':good_data['time']})
    #         fig2 = px.line(coef_df,x='original_t',y='coeffs', template='simple_white',title='Polynomial Fit')
    #         der1 = np.polyder(coefs,1)
    #         print('der1: ',der1)
    #         der1_df = pd.DataFrame.from_dict({'time':time,
    #                                             'der1':np.polyval(der1,time),
    #                                             'original_t':good_data['time']})
    #         fig3 = px.line(der1_df,x='original_t',y='der1',template='simple_white',title='First Derivative')
    #         der2 = np.polyder(coefs,2)
    #         print('der2: ',der2) 
    #         der2_df = pd.DataFrame.from_dict({'time':time,
    #                                             'der2':np.polyval(der2,time),
    #                                             'original_t':good_data['time']})
    #         fig4 = px.line(der2_df,x='original_t',y='der2',template='simple_white',title='Second Derivative')
    #         bt = Backtest(results[ticker], SmaCross, cash=10_000, commission=.002)
    #         stats = bt.optimize(n1=range(5, 50, 5),
    #                 n2=range(10, 200, 5),
    #                 maximize='Equity Final [$]',
    #                 constraint=lambda param: param.n1 < param.n2)
    #         eq_curve = stats._equity_curve
    #         eq_curve['time'] = eq_curve.index
    #         fig5 = px.line(eq_curve,x='time',y='Equity',template='simple_white')
    #         coefs = str(coefs)
    #         xx = [int(x) for x in str(stats._strategy).split() is x.isdigit()]

    #         smac = str(stats._strategy)
    #         fig1.add_trace(Scatter(x=time,y=SMA(good_data['Open'],stats._strategy[0])))
    #         fig1.add_trace(Scatter(x=time,y=SMA(good_data['Open'],stats._strategy[1])))
    #     except exceptions.YahooFinanceError:
    #         fig1,fig2,fig3,fig4,fig5 = 'No Ticker Available'
    #     return fig1, fig2, fig3, fig4, fig5, coefs, smac

    # app.run_server(debug=True)


