# data.py - helper for fetching Binance OHLCV data

import pandas as pd
import requests

def get_binance_data(symbol, interval):
    """
    Fetch recent OHLCV candlestick data from Binance API.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., 'BTCUSDT').
        interval (str): Time interval (e.g., '5m', '1h').

    Returns:
        pd.DataFrame: DataFrame indexed by timestamp with columns:
                      open, high, low, close, volume (all floats).
                      Returns None if fetch fails.
    """
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100'
    try:
        response = requests.get(url)
        data = response.json()

        # Create DataFrame with relevant columns only
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            '_', '_', '_', '_', '_', '_'
        ])

        # Convert timestamp to datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Convert price columns to floats
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)

        return df

    except Exception as e:
        print("Error fetching data:", e)
        return None
