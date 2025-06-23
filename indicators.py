import pandas as pd
import ta

def calculate_signals(df: pd.DataFrame) -> str:
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ma50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()

    latest = df.iloc[-1]

    if latest['rsi'] < 45 and latest['close'] > latest['ma50']:
        return "BUY"
    elif latest['rsi'] > 55 and latest['close'] < latest['ma50']:
        return "SELL"
    return "HOLD"