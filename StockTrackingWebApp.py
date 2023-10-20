import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.graph_objects as go
import datetime as dt
from sklearn.linear_model import LinearRegression
import pandas as pd

external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

ticker=['AAPL', 'GOOG', 'META', 'AMZN']

app.layout = html.Div(
    style={'background-image': 'url("")',
           'background-size': 'cover',
           'background-position': 'left',
           'height': '100vh'},

    children=[
        html.Div(
            style={'width': '50%', 'margin': 'auto', 'padding': '10px', 'backgroundColor': 'rgba(255, 255, 255, 0.7)'},
            children=[
                html.H1('Stock portfolio web app'),
                html.H5("Hi there, this web page aims to track your portfolio, analyze it and provides you tools for the optimization"),
                html.Label('Stock(s)'),
                dcc.Dropdown(options=[{'label': i, 'value': i} for i in ticker], multi=True, id='stock_dropdown'),

                html.Label('Start Date'),
                dcc.Input(id='start_date', value='', type='text'),
                html.Label('End Date'),
                dcc.Input(id='end_date', value=dt.datetime.now().strftime("%Y-%m-%d"), type='text'),

                html.Label('Indicators'),
                dcc.Dropdown(
                    id='indicator_dropdown',
                    options=[
                        {'label': 'Candlestick Chart', 'value': 'candlestick'},
                        {'label': '50 Days Moving Average', 'value': '50_moving_average'},
                        {'label': '20 Days Moving Average', 'value': '20_moving_average'},
                        {'label': 'Relative Strength Index (RSI)', 'value': 'rsi'},
                        {'label': 'Moving Average Convergence Divergence (MACD)', 'value': 'macd'}
                    ],
                    value=[],
                    multi=True
                ),
                html.Button('Load Data', id='load-button', n_clicks=0),
            ],
            className='six columns',
            
        ),
        html.Div(id='output-graphs', className='six columns', style={'float': 'center'})
    ],
    className='row'
)


@app.callback(
    Output('output-graphs', 'children'),
    [Input('load-button', 'n_clicks')],
    [Input('stock_dropdown', 'value'),
     Input('start_date', 'value'),
     Input('end_date', 'value'),
     Input('indicator_dropdown', 'value')]
)
def update_output(n_clicks, selected_stock, start_date, end_date, indicators):
    graphs = []
    if n_clicks > 0:
        for stock in selected_stock:
            df = yf.download(stock, start=start_date, end=end_date)

            fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Close'])])
            fig.update_layout(title=f"Candlestick Chart for {stock}")

            if '50_moving_average' in indicators:
                df['50_Day_MA'] = df['Close'].rolling(window=50).mean()
                fig.add_trace(go.Scatter(x=df.index, y=df['50_Day_MA'], mode='lines', name='50 Days Moving Average'))

            if '20_moving_average' in indicators:
                df['20_Day_MA'] = df['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=df.index, y=df['20_Day_MA'], mode='lines', name='20 Days Moving Average'))

            graphs.append(dcc.Graph(figure=fig))

    return graphs


if __name__ == '__main__':
    app.run_server(debug=True)
