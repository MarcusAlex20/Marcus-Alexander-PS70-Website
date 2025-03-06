-*import ccxt
import time
import logging
import threading
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exchange API keys (replace with real keys)
BINANCE_API_KEY = "your_binance_api_key"
BINANCE_SECRET = "your_binance_secret"

KRAKEN_API_KEY = "your_kraken_api_key"
KRAKEN_SECRET = "your_kraken_secret"

# Initialize exchange clients
binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET
})

kraken = ccxt.kraken({
    'apiKey': KRAKEN_API_KEY,
    'secret': KRAKEN_SECRET
})

# Stablecoin trading pair
PAIR = "USDT/USDC"

# Ledger file
LEDGER_FILE = "trade_ledger.json"

def load_ledger():
    """Load trade ledger from a JSON file."""
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as file:
            return json.load(file)
    return {"trades": [], "average_profit": 0.0}  # If no ledger exists, create a fresh start

def save_ledger(ledger_data):
    """Save trade ledger to a JSON file."""
    with open(LEDGER_FILE, "w") as file:
        json.dump(ledger_data, file, indent=4)

def update_ledger(buy_price, sell_price, amount):
    """Update the ledger with a new trade and calculate the running average profit."""
    ledger_data = load_ledger()
    profit = (sell_price - buy_price) * amount
    ledger_data["trades"].append({"buy_price": buy_price, "sell_price": sell_price, "amount": amount, "profit": profit})
    
    total_profit = sum(trade["profit"] for trade in ledger_data["trades"])
    ledger_data["average_profit"] = total_profit / len(ledger_data["trades"])
    
    save_ledger(ledger_data)
    logging.info(f"Trade recorded: Buy at {buy_price}, Sell at {sell_price}, Amount: {amount}, Profit: {profit}")
    logging.info(f"Running average profit: {ledger_data['average_profit']}")

def get_prices():
    """Fetches bid-ask prices from both exchanges."""
    try:
        binance_ticker = binance.fetch_ticker(PAIR)
        kraken_ticker = kraken.fetch_ticker(PAIR)

        binance_bid = binance_ticker['bid']
        binance_ask = binance_ticker['ask']
        kraken_bid = kraken_ticker['bid']
        kraken_ask = kraken_ticker['ask']

        return {
            "binance": {"bid": binance_bid, "ask": binance_ask},
            "kraken": {"bid": kraken_bid, "ask": kraken_ask}
        }
    except Exception as e:
        logging.error(f"Error fetching prices: {e}")
        return None

def execute_trade(buy_exchange, sell_exchange, amount):
    """Executes buy on one exchange and sell on another."""
    try:
        # Execute buy and sell orders in parallel
        buy_thread = threading.Thread(target=buy_exchange.create_market_buy_order, args=(PAIR, amount))
        sell_thread = threading.Thread(target=sell_exchange.create_market_sell_order, args=(PAIR, amount))
        
        buy_thread.start()
        sell_thread.start()
        
        buy_thread.join()
        sell_thread.join()
        
        buy_price = buy_exchange.fetch_ticker(PAIR)['ask']
        sell_price = sell_exchange.fetch_ticker(PAIR)['bid']
        
        update_ledger(buy_price, sell_price, amount)
        
        logging.info(f"Executed trade: Buy on {buy_exchange.name}, Sell on {sell_exchange.name}")
    except Exception as e:
        logging.error(f"Error executing trade: {e}")

def calculate_potential_profit(buy_price, sell_price, amount):
    """Calculate potential profit from a trade."""
    return (sell_price - buy_price) * amount

def arbitrage():
    """Checks for arbitrage opportunities and executes trades."""
    while True:
        prices = get_prices()
        if prices:
            binance_ask = prices["binance"]["ask"]
            kraken_bid = prices["kraken"]["bid"]
            kraken_ask = prices["kraken"]["ask"]
            binance_bid = prices["binance"]["bid"]

            # Arbitrage conditions
            if kraken_bid > binance_ask:  # Buy on Binance, sell on Kraken
                potential_profit = calculate_potential_profit(binance_ask, kraken_bid, 100)  # Example amount
                if potential_profit > 0:  # Ensure there is a profit to be made
                    logging.info(f"Arbitrage Opportunity: Buy on Binance at {binance_ask}, Sell on Kraken at {kraken_bid}, Potential Profit: {potential_profit}")
                    execute_trade(binance, kraken, 100)  # Example amount

            elif binance_bid > kraken_ask:  # Buy on Kraken, sell on Binance
                potential_profit = calculate_potential_profit(kraken_ask, binance_bid, 100)  # Example amount
                if potential_profit > 0:  # Ensure there is a profit to be made
                    logging.info(f"Arbitrage Opportunity: Buy on Kraken at {kraken_ask}, Sell on Binance at {binance_bid}, Potential Profit: {potential_profit}")
                    execute_trade(kraken, binance, 100)  # Example amount

        time.sleep(1)  # Short delay to avoid API rate limits

if __name__ == "__main__":
    arbitrage()
