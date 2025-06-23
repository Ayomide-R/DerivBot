import csv

with open("trades.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "signal", "price", "contract_id"])

print("✅ trades.csv header created.")