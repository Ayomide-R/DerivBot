# Deriv Trading Bot

This is a machine learning-powered trading bot for Deriv's Volatility markets.

## Features
- ML prediction (RandomForest)
- Take Profit / Stop Loss
- Trade logging
- Daily trade limits
- .env for secure credentials

## Setup
1. Create a `.env` file with:
APP_ID=your_app_id
API_TOKEN=your_api_token
MARKET=volatility_75_index

2. Install dependencies:
```bash
pip install -r requirements.txt

3. Run Bot
python main.py