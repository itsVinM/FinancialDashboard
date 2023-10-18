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



app.layout = html.Div(
    style={'background-image': 'url("https://example.com/background-image.jpg")',
           'background-size': 'cover',
           'background-position': 'center',
           'height': '100vh'},
    children=[
        html.Div(
            style={'width': '50%', 'margin': 'auto', 'padding': '10px', 'backgroundColor': 'rgba(255, 255, 255, 0.7)'},
            children=[
                html.H1('Financial Analytics'),
                html.Label('Stock 1'),
                dcc.Input(id='stock1', value='', type='text'),
                html.Label('Stock 2'),
                dcc.Input(id='stock2', value='', type='text'),
                html.Label('Start Date'),
                dcc.Input(id='start_date', value='', type='text'),
                html.Label('End Date'),
                dcc.Input(id='end_date', value=dt.datetime.now().strftime("%Y-%m-%d"), type='text'),
                html.Label('Indicators'),
                dcc.Dropdown(
                    id='indicator_dropdown',
                    options=[
                        {'label': 'Candlestick Chart', 'value': 'candlestick'},
                        {'label': 'Linear Regression', 'value': 'linear_regression'},
                        {'label': '50 Days Moving Average', 'value': '50_moving_average'},
                        {'label': '20 Days Moving Average', 'value': '20_moving_average'}
                    ],
                    value=[],
                    multi=True
                ),
                html.Button('Load Data', id='load-button', n_clicks=0),
                html.Div(id='output-graphs')
            ]
        )
    ]
)


@app.callback(
    Output('output-graphs', 'children'),
    [Input('load-button', 'n_clicks')],
    [Input('stock1', 'value'),
     Input('stock2', 'value'),
     Input('start_date', 'value'),
     Input('end_date', 'value'),
     Input('indicator_dropdown', 'value')]
)
def update_output(n_clicks, stock1, stock2, start_date, end_date, indicators):
    if n_clicks > 0:
        df1 = yf.download(stock1, start=start_date, end=end_date)
        df2 = yf.download(stock2, start=start_date, end=end_date)

        fig1 = go.Figure(data=[go.Candlestick(x=df1.index,
                                             open=df1['Open'],
                                             high=df1['High'],
                                             low=df1['Low'],
                                             close=df1['Close'])])
        fig1.update_layout(title=f"Candlestick Chart for {stock1}")

        fig2 = go.Figure(data=[go.Candlestick(x=df2.index,
                                             open=df2['Open'],
                                             high=df2['High'],
                                             low=df2['Low'],
                                             close=df2['Close'])])
        fig2.update_layout(title=f"Candlestick Chart for {stock2}")

        if 'linear_regression' in indicators:
            lr = LinearRegression()
            lr.fit(pd.to_datetime(df1.index).map(dt.datetime.toordinal).values.reshape(-1, 1), df1['Close'].values)
            df1['Linear_Regression'] = lr.predict(pd.to_datetime(df1.index).map(dt.datetime.toordinal).values.reshape(-1, 1))
            fig1.add_trace(go.Scatter(x=df1.index, y=df1['Linear_Regression'], mode='lines', name='Linear Regression'))

            lr.fit(pd.to_datetime(df2.index).map(dt.datetime.toordinal).values.reshape(-1, 1), df2['Close'].values)
            df2['Linear_Regression'] = lr.predict(pd.to_datetime(df2.index).map(dt.datetime.toordinal).values.reshape(-1, 1))
            fig2.add_trace(go.Scatter(x=df2.index, y=df2['Linear_Regression'], mode='lines', name='Linear Regression'))

        if '50_moving_average' in indicators:
            df1['50_Day_MA'] = df1['Close'].rolling(window=50).mean()
            fig1.add_trace(go.Scatter(x=df1.index, y=df1['50_Day_MA'], mode='lines', name='50 Days Moving Average'))

            df2['50_Day_MA'] = df2['Close'].rolling(window=50).mean()
            fig2.add_trace(go.Scatter(x=df2.index, y=df2['50_Day_MA'], mode='lines', name='50 Days Moving Average'))

        if '20_moving_average' in indicators:
            df1['20_Day_MA'] = df1['Close'].rolling(window=20).mean()
            fig1.add_trace(go.Scatter(x=df1.index, y=df1['20_Day_MA'], mode='lines', name='20 Days Moving Average'))

    return [
                dcc.Graph(figure=fig1),
                dcc.Graph(figure=fig2)
    ]


if __name__ == '__main__':
    app.run_server(debug=True)

