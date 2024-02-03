import streamlit as st
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import os

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
coln1, coln2, coln3 = st.columns(3)
with coln1:
    selected_stocks = st.multiselect("Select stocks:", ticker, default=ticker[0])
with coln2:
    start_date = st.date_input("Start date", dt.datetime(2022, 1, 1))
with coln3:
    end_date = st.date_input("End date", dt.datetime.now())

# Sidebar for analysis selection
selected_analysis = st.sidebar.selectbox("Select Analysis", ["Close", "Candlestick", "Bollinger Bands", "50-day SMA", "20-day SMA"])

# Download stock data
def download_stock_data(stock, start_date, end_date):
     return yf.download(stock, start=start_date, end=end_date)['Close']

# Create a common figure for charts
fig = go.Figure()

# Portfolio data
portfolio_file = "portfolio.xlsx"
if not os.path.isfile(portfolio_file):
    pd.DataFrame(columns=["Stock", "Quantity"]).to_excel(portfolio_file, index=False)

# Load the existing portfolio
portfolio = pd.read_excel(portfolio_file)

# Sidebar input for constructing the portfolio
st.sidebar.title("Portfolio Construction")

# Iterate through selected stocks and add traces to the common figure
for stock in selected_stocks:
    with st.sidebar.expander(f"Manage {stock} in Your Portfolio"):
        quantity = st.number_input(f"Enter the quantity of {stock}:", min_value=0, step=1, key=f"{stock}_quantity")
        add_to_portfolio = st.button(f"Add {stock} to Portfolio", key=f"{stock}_add_button")
        subtract_from_portfolio = st.button(f"Subtract {stock} from Portfolio", key=f"{stock}_subtract_button")

        if add_to_portfolio:
            existing_entry = portfolio[portfolio['Stock'] == stock]
            if not existing_entry.empty:
                portfolio.loc[existing_entry.index, 'Quantity'] += quantity
            else:
                new_entry = pd.DataFrame({"Stock": [stock], "Quantity": [quantity]})
                portfolio = pd.concat([portfolio, new_entry], ignore_index=True)

        if subtract_from_portfolio:
            existing_entry = portfolio[portfolio['Stock'] == stock]
            if not existing_entry.empty and existing_entry['Quantity'].values[0] >= quantity:
                portfolio.loc[existing_entry.index, 'Quantity'] -= quantity

# Iterate through selected stocks and add traces to the common figure
for stock in selected_stocks:
    df = download_stock_data(stock, start_date, end_date)

    # Add traces based on the selected analysis
    if selected_analysis == "Close":
        fig.add_trace(go.Scatter(x=df.index, y=df, name=f"{stock} - Close"))
    elif selected_analysis == "Candlestick":
        fig.add_trace(go.Candlestick(x=df.index, open=df, high=df, low=df, close=df, name=f"{stock} - Candlestick"))
    elif selected_analysis == "Bollinger Bands":
        # Add Bollinger Bands
        rolling_mean = df.rolling(window=20).mean()
        rolling_std = df.rolling(window=20).std()
        fig.add_trace(go.Scatter(x=df.index, y=rolling_mean, mode='lines', name=f"{stock} - 20 Day Bollinger Band - Mean"))
        fig.add_trace(go.Scatter(x=df.index, y=rolling_mean + 2 * rolling_std, mode='lines', name=f"{stock} - 20 Day Bollinger Band - Upper"))
        fig.add_trace(go.Scatter(x=df.index, y=rolling_mean - 2 * rolling_std, mode='lines', name=f"{stock} - 20 Day Bollinger Band - Lower"))
    elif selected_analysis == "50-day SMA":
        # Add 50-day SMA
        fig.add_trace(go.Scatter(x=df.index, y=df.rolling(window=50).mean(), mode='lines', name=f"{stock} - 50 Day SMA"))
    elif selected_analysis == "20-day SMA":
        # Add 20-day SMA
        fig.add_trace(go.Scatter(x=df.index, y=df.rolling(window=20).mean(), mode='lines', name=f"{stock} - 20 Day SMA"))

# Update the layout for common elements
fig.update_layout(title=f"{selected_analysis} - Financial Dashboard", xaxis_title='Date', yaxis_title='Price', height=500, width=1800)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

# Display portfolio table
st.sidebar.title("Current Portfolio")
st.sidebar.dataframe(portfolio)

# Save the updated portfolio
portfolio.to_excel(portfolio_file, index=False)

# Perform Portfolio Analysis using pypfopt
st.sidebar.title("Portfolio Analysis")


# Button to trigger the analysis
if st.sidebar.button("Analyze Portfolio"):
    if not portfolio.empty:
        # Download historical data for the portfolio stocks
        portfolio_data = {stock: download_stock_data(stock, start_date, end_date)['Close'] for stock in portfolio['Stock']}

        # Convert portfolio data to DataFrame
        portfolio_df = pd.DataFrame(portfolio_data)

        # Calculate the Expected Returns
        expected_returns = expected_returns.mean_historical_return(portfolio_df)

        # Display the expected returns
        st.sidebar.write("### Expected Returns")
        st.sidebar.table(expected_returns)

        # Check if any asset has expected return less than risk-free rate
        if not (expected_returns > 0.02).any():
            st.warning("Warning: At least one asset must have an expected return exceeding the risk-free rate.")
        else:
            # Build the portfolio using pypfopt
            mu = expected_returns
            S = risk_models.sample_cov(portfolio_df)
            ef = EfficientFrontier(mu, S)

            # Calculate the Efficient Frontier
            #weights = ef.max_sharpe(risk_free_rate=0.02)
            cleaned_weights = ef.clean_weights()

            # Get latest prices for asset allocation
            latest_prices = get_latest_prices(portfolio_df)

            # Perform Discrete Allocation
            da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value=10000)
            allocation, leftover = da.lp_portfolio()

            # Display key metrics
            st.sidebar.write("### Portfolio Metrics")
            st.sidebar.write(f"Total Portfolio Value: ${sum(allocation.values()):,.2f}")
            st.sidebar.write(f"Expected Annual Return: {ef.portfolio_performance(expected_returns=mu, risk_free_rate=0.02)[0]:.2%}")
            st.sidebar.write(f"Expected Volatility: {ef.portfolio_performance(expected_returns=mu, risk_free_rate=0.02)[1]:.2%}")
            st.sidebar.write(f"Sharpe Ratio: {ef.portfolio_performance(expected_returns=mu, risk_free_rate=0.02)[2]:.4f}")

            # Display the Efficient Frontier plot
            st.sidebar.plotly_chart(ef.plot_efficient_frontier())

            # Display the portfolio weights
            st.sidebar.write("### Portfolio Weights")
            st.sidebar.table(cleaned_weights)

            # Display Discrete Allocation results
            st.sidebar.write("### Discrete Allocation")
            st.sidebar.write(f"Amount to invest: ${10000 - leftover:.2f}")
            st.sidebar.table(allocation)
