import dash
from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.graph_objects as go
import datetime as dt
import pandas as pd
import finquant
import json

    
with open('sp500_tickers.json', 'r') as f:
    ticker = json.load(f)

external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
   
app.layout = html.Div(
    
    style={'background-image': 'url("")',
           'background-size': 'cover',
           'background-position': 'left',
           'height': '100vh'},

    children=[
        html.Div(
            className='six columns',
            style={'float': 'left'},
            children=[
                html.H1('Stock Analytics'),

                html.Label('Stock(s)'),
                dcc.Dropdown(options=[{'label': i, 'value': i} for i in ticker], multi=True, id='stock_dropdown'),

                html.Label('Start Date'),
                dcc.Input(id='start_date', value='', type='text'),
                html.Label('End Date'),
                dcc.Input(id='end_date', value=dt.datetime.now().strftime("%Y-%m-%d"), type='text'),

                html.Button('Load Data', id='load-button', n_clicks=0),
            ],
        ),
        html.Div(id='output-graphs', className='six columns', style={'float': 'left'}),
        html.Div([
            html.Label('Additional Plot'),
            dcc.Dropdown(id='dynamic-dropdown')
        ], style={'width': '30%', 'margin-left': '5%'})
    ],
    className='row',
)
        
@app.callback(
    [Output('output-graphs', 'children'),
     Output('dynamic-dropdown', 'options')],
    [Input('load-button', 'n_clicks')],
    [Input('stock_dropdown', 'value'),
     Input('start_date', 'value'),
     Input('end_date', 'value')]
)
def update_output(n_clicks, selected_stock, start_date, end_date):
    graphs = []
    dropdown_options = []
    if n_clicks > 0:
        fig = go.Figure()
        for stock in selected_stock:
            df = yf.download(stock, start=start_date, end=end_date)
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name=stock))
            dropdown_options.append({'label': stock, 'value': stock})

        fig.update_layout(title='Stock Prices',
                          xaxis_title='Date',
                          yaxis_title='Price')

        graphs.append(dcc.Graph(figure=fig))

    return graphs, dropdown_options


if __name__ == '__main__':
    app.run_server(debug=True)
