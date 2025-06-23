# main.py

import websocket, json, pandas as pd, time
from config import APP_ID, API_TOKEN, MARKET
from logger import log_trade
import joblib
import ta
print(f"APP_ID: {APP_ID}, API_TOKEN: {API_TOKEN}, MARKET: {MARKET}")

data_window = []
authorized = False
current_contract_id = None
entry_price = None
entry_signal = None
trade_count = 0
MAX_DAILY_TRADES = 5

# ✅ Load ML Model
model = joblib.load("model.pkl")

def calculate_ml_signal(df: pd.DataFrame) -> str:
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ma50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
    df = df.dropna()

    # ✅ Safe guard: if df is empty after indicators
    if df.empty or len(df) < 1:
        return "HOLD"

    # ✅ Extract last row cleanly with correct features
    latest = df[['close', 'rsi', 'ma50']].iloc[-1]
    latest_df = pd.DataFrame([latest], columns=['close', 'rsi', 'ma50'])

    # ✅ Predict using trained model
    prediction = model.predict(latest_df)[0]

    if prediction == 1:
        return "BUY"
    elif prediction == -1:
        return "SELL"
    return "HOLD"

def send_buy_order(ws, direction, price):
    global current_contract_id, entry_price, entry_signal, trade_count

    if trade_count >= MAX_DAILY_TRADES:
        print("🚫 Max trades reached for the day.")
        return

    contract_type = "CALL" if direction == "BUY" else "PUT"
    print(f"🟢 Placing {direction} trade...")

    ws.send(json.dumps({
        "buy": 1,
        "price": 1,
        "parameters": {
            "amount": 1,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": 1,
            "duration_unit": "m",
            "symbol": MARKET
        }
    }))

    entry_price = price
    entry_signal = direction
    trade_count += 1

def simulate_tp_sl(current_price):
    global entry_price, entry_signal
    if not entry_price or not entry_signal:
        return

    change = (current_price - entry_price) / entry_price * 100
    if entry_signal == "BUY":
        if change >= 1.5:
            print("🎯 Take Profit Hit!")
            entry_price = None
        elif change <= -0.75:
            print("🛑 Stop Loss Hit!")
            entry_price = None

    elif entry_signal == "SELL":
        if change <= -1.5:
            print("🎯 Take Profit Hit!")
            entry_price = None
        elif change >= 0.75:
            print("🛑 Stop Loss Hit!")
            entry_price = None

def on_message(ws, message):
    global data_window, authorized, current_contract_id

    msg = json.loads(message)

    if "error" in msg:
        print("❌ Error:", msg["error"]["message"])
        return

    if msg.get("msg_type") == "authorize":
        authorized = True
        print("🔐 Authorized successfully. Listening to live ticks...")
        ws.send(json.dumps({
            "ticks": MARKET,
            "subscribe": 1
        }))

    elif msg.get("msg_type") == "tick":
        tick = msg["tick"]
        price = float(tick["quote"])
        timestamp = tick["epoch"]

        data_window.append({"timestamp": timestamp, "close": price})
        if len(data_window) > 100:
            df = pd.DataFrame(data_window[-100:])
            signal = calculate_ml_signal(df)
            print(f"[{timestamp}] ML Signal: {signal} | Price: {price}")
            simulate_tp_sl(price)

            if signal in ["BUY", "SELL"] and not current_contract_id:
                send_buy_order(ws, signal, price)

    elif msg.get("msg_type") == "buy":
        current_contract_id = msg["buy"]["contract_id"]
        print(f"✅ Trade placed. Contract ID: {current_contract_id}")
        log_trade(entry_signal, entry_price, current_contract_id)

def on_open(ws):
    print("🔄 Connecting and authorizing...")
    ws.send(json.dumps({"authorize": APP_ID}))

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, code, reason):
    print("🔒 WebSocket closed:", code, reason)

if __name__ == "__main__":
    socket_url = f"wss://ws.deriv.com/websockets/v3?app_id={APP_ID}"
    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()