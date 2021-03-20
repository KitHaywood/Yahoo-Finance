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

class TickerTable:
    def __init__(self):
        super().__init__()
    
    def getTable(self):
        self.url = 'https://en.wikipedia.org/wiki/FTSE_100_Index#cite_note-13'
        self.html = requests.get(self.url).content
        self.df_list = pd.read_html(self.html)[3]
        return self.df_list
    
class GetTickerData:
    def __init__(self):
        super().__init__()

    def get_data(self,ticker):
        self.ticker = ticker
        print(type(self.ticker))
        print('in get_data',self.ticker)
        if isinstance(self.ticker,str):
            print('took_str_option')
            self.my_share = share.Share(self.ticker)
            self.data = self.my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                    10,
                                                    share.FREQUENCY_TYPE_MINUTE,
                                                    5)
            self.result = list(zip(self.data['timestamp'],self.data['open']))
            self.result = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in self.result]  
            return self.result

        elif isinstance(self.ticker,list):
            print('took_list_option')
            self.my_share = share.Share(self.ticker)
            self.data = self.my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                    10,
                                                    share.FREQUENCY_TYPE_MINUTE,
                                                    5)
            self.result = list(zip(self.data['timestamp'],self.data['open']))
            self.result = [(dt.datetime.fromtimestamp(x[0]/1000),x[1]) for x in self.result]
            return self.result
        

class App(GetTickerData):
    def __init__(self,ticker):
        super().__init__()
        self.result = GetTickerData
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div([
            dcc.Graph(id='line-chart')])
        
# @app.callback(
#     Output("line-chart", "figure"), 
# [Input("checklist", "value")] # will break here 
# )

if __name__=="__main__":

    df = px.data.gapminder().query("continent=='Oceania'")
    fig = px.line(df, x="year", y="lifeExp", color='country')
    ex_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    wiki_data = TickerTable().getTable()
    tickers = list(wiki_data['EPIC'])

    print(tickers)
    my_share = share.Share('AAL')
    data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                                    10,
                                                    share.FREQUENCY_TYPE_MINUTE,
                                                    5)
    # print(data.keys())
    # print('Calling Classes')
    # print(GetTickerData().get_data('AAL'))
    test_ts = GetTickerData().get_data('AAL')

    # print('test_ts:',test_ts)
    
    my_df = pd.DataFrame.from_dict({
        'time':[x[1] for x in test_ts],
        'value':[x[0] for x in test_ts]
    })
    print(my_df)

    my_fig = px.line(my_df,x='time',y='value')
    my_fig.show()
    df = px.data.gapminder()
    type_df = df.applymap(lambda x: type(x))
    all_continents = df.continent.unique()
            # def update_line_chart(self,ticker):
            # self.mask = self.result.continent.isin(ticker)
            # self.fig = px.line(self.[mask], 
            #     x='Date', y="price", color=ticker)
            # return fig

    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(figure=fig),
    ])
    @app.callback(
        Output("line-chart", "figure"), 
        [Input("checklist", "value")])
    def update_line_chart(continents):
        mask = df.continent.isin(continents)
        fig = px.line(df[mask], 
            x="year", y="lifeExp", color='country')
        return fig
    app.run_server(debug=True)