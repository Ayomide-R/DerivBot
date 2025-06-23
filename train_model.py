import pandas as pd
import ta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Step 1: Load your historical data
df = pd.read_csv("historical_data.csv")

# Step 2: Add indicators
df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
df['ma50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()

# Step 3: Drop NaNs caused by indicators
df = df.dropna()

# Step 4: Label data (target column)
def generate_signal(row):
    if row['rsi'] < 45 and row['close'] > row['ma50']:
        return 1  # BUY
    elif row['rsi'] > 55 and row['close'] < row['ma50']:
        return -1  # SELL
    else:
        return 0  # HOLD

df['signal'] = df.apply(generate_signal, axis=1)

# Step 5: Features and labels
features = df[['close', 'rsi', 'ma50']]
labels = df['signal']

# Step 6: Split into train and test
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Step 7: Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 8: Evaluate model
y_pred = model.predict(X_test)
print("📊 Classification Report:\n", classification_report(y_test, y_pred))

# Step 9: Save model to file
joblib.dump(model, "model.pkl")
print("✅ Model saved as model.pkl")
