# data_collector.py

import websocket
import json
import pandas as pd

SYMBOL = "R_75"
CANDLE_COUNT = 1000

def on_message(ws, message):
    print("📩 Message received.")
    msg = json.loads(message)
    
    if msg.get("msg_type") == "candles":
        candles = msg["candles"]
        print(f"✅ Received {len(candles)} candles.")

        df = pd.DataFrame(candles)
        df['epoch'] = pd.to_datetime(df['epoch'], unit='s')
        df.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close'}, inplace=True)
        df.to_csv("historical_data.csv", index=False)

        print("✅ historical_data.csv saved.")
        ws.close()
    elif "error" in msg:
        print("❌ Error:", msg["error"]["message"])
        ws.close()

def on_open(ws):
    print("🔄 Connected to Deriv API...")
    ws.send(json.dumps({
        "ticks_history": SYMBOL,
        "adjust_start_time": 1,
        "count": CANDLE_COUNT,
        "end": "latest",
        "style": "candles",
        "granularity": 60
    }))

def collect_data():
    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3?app_id=82277",
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()

if __name__ == "__main__":
    collect_data()