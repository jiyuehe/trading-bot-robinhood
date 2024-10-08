from pyrh import Robinhood
from datetime import datetime
import numpy as np
import tulipy as ti
import sched
import time

# A Simple Robinhood Python Trading Bot using RSI (buy <=30 and sell >=70 RSI) and with support and resistance.

# Relative Strength Index (RSI): The Relative Strength Index indicator is a line whose value moves between 0 to 100
# and tries to indicate whether a stock is under- or overvalued based on the magnitude of recent changes in the price
# of the stock. Values below 30 are thought to indicate that a stock is undervalued (i.e. oversold). Values above 70
# are thought to indicate that a stock is overvalued (i.e. overbought).

# Log in to Robinhood app (will prompt for two-factor)
rh = Robinhood()
rh.login(username="", password="")

# haven't entered a trade yet
entered_trade = False
# RSI period
rsi_period = 5
# Initiate our scheduler so we can keep checking every minute for new price changes
s = sched.scheduler(time.time, time.sleep)

def run(sc):
    global entered_trade
    global rsi_period

    print("Getting historical quotes")
    # Get 5 minute bar data for Ford stock
    historical_quotes = rh.get_historical_quotes("F", "5minute", "day")

    # format close prices for RSI
    close_prices = []
    current_index = 0
    current_support = 0
    current_resistance = 0

    for key in historical_quotes["results"][0]["historicals"]:
        if (current_index >= len(historical_quotes["results"][0]["historicals"]) - (rsi_period + 1)):
            if (current_index >= (rsi_period-1) and datetime.strptime(key['begins_at'], '%Y-%m-%dT%H:%M:%SZ').minute == 0):
                current_support = 0
                current_resistance = 0
                print("Resetting support and resistance")
            if(float(key['close_price']) < current_support or current_support == 0):
                current_support = float(key['close_price'])
                print("Current Support is : ")
                print(current_support)
            if(float(key['close_price']) > current_resistance):
                current_resistance = float(key['close_price'])
                print("Current Resistance is : ")
                print(current_resistance)
            close_prices.append(float(key['close_price']))
        current_index = current_index + 1

    DATA = np.array(close_prices)

    if (len(close_prices) > (rsi_period)):
        # Calculate RSI
        rsi = ti.rsi(DATA, period=rsi_period)
        instrument = rh.instruments("F")[0]
        # If rsi is less than or equal to 30 buy
        if rsi[len(rsi) - 1] <= 30 and float(key['close_price']) <= current_support and not entered_trade:
            print("Buying RSI is below 30!")
            rh.place_buy_order(instrument, 1)
            entered_trade = True
        # Sell when RSI reaches 70
        if rsi[len(rsi) - 1] >= 70 and float(key['close_price']) >= current_resistance and current_resistance > 0 and entered_trade:
            print("Selling RSI is above 70!")
            rh.place_sell_order(instrument, 1)
            entered_trade = False
        print(rsi)

    # call this method again every 5 minutes for new price changes
    s.enter(300, 1, run, (sc,))


s.enter(1, 1, run, (s,))
s.run()
