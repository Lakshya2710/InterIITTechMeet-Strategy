import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
data = pd.read_csv(r"C:\Users\mohin\Downloads\S5\QUANT\btcusdt_30m.csv")

# Rename columns to match the expected format
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Parse the datetime column and set as index
data['Date'] = pd.to_datetime(data['datetime'], errors='coerce')
data.dropna(subset=['Date'], inplace=True)
data.set_index('Date', inplace=True)

# Manually resample the data to 1-hour frequency
data_resampled = data.resample('1H').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# Calculate Simple Moving Averages
short_window = 10  # Short moving average window
long_window = 30   # Long moving average window

data_resampled['SMA_Short'] = data_resampled['Close'].rolling(window=short_window).mean()
data_resampled['SMA_Long'] = data_resampled['Close'].rolling(window=long_window).mean()

# Initialize trading signals
data_resampled['Signal'] = 0
data_resampled['Signal'][short_window:] = np.where(data_resampled['SMA_Short'][short_window:] > data_resampled['SMA_Long'][short_window:], 1, 0)
data_resampled['Position'] = data_resampled['Signal'].diff()

# Set initial parameters for simulation
initial_capital = 100000  # Starting capital
shares = 0  # Number of shares currently held
cash = initial_capital  # Cash balance

# Lists to hold performance metrics
dates = []
portfolio_values = []
trade_values = []
max_portfolio_value = initial_capital  # Track max portfolio value for drawdown calculation

# Simulate trading
for date, row in data_resampled.iterrows():
    # Calculate portfolio value before any transactions
    portfolio_value = cash + shares * row['Close']  # Total portfolio value
    portfolio_values.append(portfolio_value)
    max_portfolio_value = max(max_portfolio_value, portfolio_value)  # Update max portfolio value

    # Buy signal
    if row['Position'] == 1:
        shares = cash // row['Close']  # Buy as many shares as possible
        cash -= shares * row['Close']  # Reduce cash by the amount spent
        trade_values.append(shares * row['Close'])  # Record the value of the trade
        print(f"Buying {shares} shares at {row['Close']} on {date}")

    # Sell signal
    elif row['Position'] == -1 and shares > 0:
        cash += shares * row['Close']  # Sell all shares
        trade_values.append(-shares * row['Close'])  # Record the value of the trade (negative for selling)
        print(f"Selling {shares} shares at {row['Close']} on {date}")
        shares = 0  # Reset shares held

# Final portfolio value
final_value = cash + shares * data_resampled['Close'].iloc[-1]
profit_loss = final_value - initial_capital  # Profit and loss
drawdown_percentage = ((max_portfolio_value - min(portfolio_values)) / max_portfolio_value) * 100 if max_portfolio_value else 0

# Turnover calculation
turnover = sum(abs(value) for value in trade_values) / (len(portfolio_values) * initial_capital) * 100  # Total turnover as percentage

print(f"\nFinal Portfolio Value: ${final_value:.2f}")
print(f"Profit and Loss: ${profit_loss:.2f}")
print(f"Turnover: {turnover:.2f}%")
print(f"Max Drawdown Percentage: {drawdown_percentage:.2f}%")
# Final portfolio value
final_value = cash + shares * data_resampled['Close'].iloc[-1]
profit_loss = final_value - initial_capital  # Profit and loss
profit_percentage = (profit_loss / initial_capital) * 100  # Calculate profit percentage
drawdown_percentage = ((max_portfolio_value - min(portfolio_values)) / max_portfolio_value) * 100 if max_portfolio_value else 0

# Turnover calculation
turnover = sum(abs(value) for value in trade_values) / (len(portfolio_values) * initial_capital) * 100  # Total turnover as percentage

print(f"\nFinal Portfolio Value: ${final_value:.2f}")
print(f"Profit and Loss: ${profit_loss:.2f}")
print(f"Profit Percentage: {profit_percentage:.2f}%")  # Print profit percentage
print(f"Turnover: {turnover:.2f}%")
print(f"Max Drawdown Percentage: {drawdown_percentage:.2f}%")


# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(data_resampled.index, data_resampled['Close'], label='BTC/USDT Price', alpha=0.5)
plt.plot(data_resampled.index, data_resampled['SMA_Short'], label='Short SMA', alpha=0.75)
plt.plot(data_resampled.index, data_resampled['SMA_Long'], label='Long SMA', alpha=0.75)
plt.title('BTC/USDT Price and Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Plot portfolio value over time
plt.figure(figsize=(12, 6))
plt.plot(data_resampled.index, portfolio_values, label='Portfolio Value', color='orange')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.legend()
plt.show()
