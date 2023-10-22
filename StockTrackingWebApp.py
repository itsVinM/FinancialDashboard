import streamlit as st
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Sample portfolio data
ticker = []
# Read the CSV file
with open('TopCompanies.csv', 'r') as file:
    for line in file:
        ticker.append(line.strip())

st.title("Financial Dashboard")
st.markdown("""
Streamlit
""")

# Input group components

coln1, coln2, coln3=st.columns(3)
with coln1:
	selected_stocks = st.multiselect("Select stocks:", ticker, default=ticker[0])
with coln2:
     start_date = st.date_input("Start date", dt.datetime(2022, 1, 1))
with coln3:
    end_date = st.date_input("End date", dt.datetime.now())

# Download stock data
def download_stock_data(stock, start_date, end_date):
    return yf.download(stock, start=start_date, end=end_date)

# Create the tabs
tab1, tab2, tab3, tab4 = st.tabs(["Charts", "Technical analysis", "Statistics", "Analysts estimates"])
st.caption("")

# Build the graph
with tab1:

	fig = go.Figure()
	for stock in selected_stocks:
	    df = download_stock_data(stock, start_date, end_date)
	    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name=stock))

	fig.update_layout(title='Stock Prices', xaxis_title='Date', yaxis_title='Price', height=500, width=1800)


	fig1 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)

	for stock in selected_stocks:
	    df = download_stock_data(stock, start_date, end_date)
	    fig1.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=f"{stock} : Candlestick"))

	    # Add Moving Averages
	    fig1.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(window=20).mean(), mode='lines', name=f"{stock} : 20 Day SMA"))

	    # Add Bollinger Bands
	    rolling_mean = df['Close'].rolling(window=20).mean()
	    rolling_50mean = df['Close'].rolling(window=50).mean()
	    rolling_std = df['Close'].rolling(window=20).std()
	    fig1.add_trace(go.Scatter(x=df.index, y=rolling_mean, mode='lines', name=f"{stock} : 20 Day Bollinger Band - Mean"))
	    fig1.add_trace(go.Scatter(x=df.index, y=rolling_50mean, mode='lines', name=f"{stock} : 50 Day Bollinger Band - Mean"))
	    fig1.add_trace(go.Scatter(x=df.index, y=rolling_mean + 2 * rolling_std, mode='lines', name=f"{stock} : 20 Day Bollinger Band - Upper"))
	    fig1.add_trace(go.Scatter(x=df.index, y=rolling_mean - 2 * rolling_std, mode='lines', name=f"{stock} : 20 Day Bollinger Band - Lower"))

	    # Add RSI
	    delta = df['Close'].diff()
	    gain = delta.mask(delta < 0, 0)
	    loss = -delta.mask(delta > 0, 0)
	    avg_gain = gain.rolling(window=14).mean()
	    avg_loss = loss.rolling(window=14).mean()
	    rs = avg_gain / avg_loss
	    rsi = 100 - (100 / (1 + rs))
	    fig1.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name=f"{stock} : RSI"))

	# Update the layout
	fig1.update_layout(
	    title='Stock Prices with Indicators',
	    xaxis_title='Date',
	    yaxis_title='Price',
	    height=1200, 
	    width=1800
	)

	# Create dropdown menu options
	buttons = []
	for stock in selected_stocks:
	    buttons.append(dict(method='update', label=stock, args=[{'visible': [stock in trace.name for trace in fig1.data]}]))

	buttons.append(dict(method='update', label='All', args=[{'visible': [True] * len(fig1.data)}]))

	# Add dropdown menu
	fig1.update_layout(
	    updatemenus=[{
		'buttons': buttons,
		'direction': 'down',
		'showactive': True,
		'x': 0.1,
		'xanchor': 'left',
		'y': 1.1,
		'yanchor': 'top'
	    }]
	)


	
# Display the graph
st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig1, use_container_width=True)
