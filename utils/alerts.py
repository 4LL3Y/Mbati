# alerts.py - simple example alert logic module

def check_ma_breach(df):
    """
    Check if the close price crossed above the MA in the last candle.

    Args:
        df (pd.DataFrame): DataFrame with columns 'close' and 'MA'.

    Returns:
        bool: True if close crossed above MA between last two data points.
    """
    if len(df) < 2:
        return False

    # Check if close price crossed from below to above MA
    return df['close'].iloc[-1] > df['MA'].iloc[-1] and df['close'].iloc[-2] <= df['MA'].iloc[-2]
