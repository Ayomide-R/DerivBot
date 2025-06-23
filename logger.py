import csv
from datetime import datetime

def log_trade(signal, price, contract_id):
    with open("trades.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            signal,
            price,
            contract_id
        ])