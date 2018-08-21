
import ccxt
import datetime
import time
import math
# import pandas as pd
import numpy as np
import pprint

# DATA FEED FROM EXCHANGE
symbol = str('BTC/USD')
timeframe = str('1d')
# exchange = str('okex')
# exchange_out = str(exchange)
start_date = str('2018-01-01')
get_data = True
order_qty = 1.0

# from variable id
exchange_id1 = 'okex'
exchange_class1 = getattr(ccxt, exchange_id1)
exchange1 = exchange_class1({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'timeout': 30000,
    'enableRateLimit': True,
})

exchange_id2 = 'deribit'
exchange_class2 = getattr(ccxt, exchange_id2)
exchange2 = exchange_class2({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'timeout': 30000,
    'enableRateLimit': True,
})

# exchange1 = ccxt.okex()
# exchange2 = ccxt.deribit()

def order_book(exchange,symbol,limit):
    exchange = getattr(ccxt, exchange)()
    exchange.load_markets()
    data = exchange.fetch_order_book(symbol,limit)
    bid = data['bids'][0][0] if len(data['bids']) > 0 else None
    ask = data['asks'][0][0] if len(data['asks']) > 0 else None
    return bid,ask

expiry = 'this_month' # Can be 'this_week','this_month','this_quarter'
reqd_spread = 0.05

def run():
    #Set Initial conditions for bot
    arbitrage()
    time.sleep(20)


def arbitrage(symbol,expiry):

    buy_order_price = 0.0
    sell_order_price = 0.0
    print("Getting Order Book for OKEX:")

    # Get Order Book for First exchange
    orderbook_exch1 = exchange1.fetch_order_book(symbol, 5, {'contract_type': expiry})

    # get bid and ask prices for First Exchange
    bid_exch1 = orderbook_exch1['bids'][0][0] if len(orderbook_exch1['bids']) > 0 else None
    ask_exch1 = orderbook_exch1['asks'][0][0] if len(orderbook_exch1['asks']) > 0 else None

    print("Getting Order Book for Deribit:")
    # Get Order Book for Second exchange
    orderbook_exch2 = exchange2.fetch_order_book(symbol, 5, {'contract_type': expiry})

    # get bid and ask prices for Second Exchange
    bid_exch2 = orderbook_exch2['bids'][0][0] if len(orderbook_exch2['bids']) > 0 else None
    ask_exch2 = orderbook_exch2['asks'][0][0] if len(orderbook_exch2['asks']) > 0 else None

    '''
    if (bid_exch1 > bid_exch2) & (bid_exch1 > ask_exch2):
        if bid_exch1 - ask_exch2 > spread_percent * bid_exch1:
            buy_order_price = ask_exch2
            sell_order_price = bid_exch1

    elif (bid_exch2 > bid_exch1) & (bid_exch2 > ask_exch1):
        if bid_exch2 - ask_exch1 > spread_percent * bid_exch2:
            buy_order_price = ask_exch1
            sell_order_price = bid_exch2

    '''
    # Sell Exchange1 Buy Exchange2
    spread1 = bid_exch1 - ask_exch2
    print ("Sell Exchange1 Buy Exchange2 - Spread:", spread1)

    # Sell Exchange2 Buy Exchange1
    spread2 = bid_exch2 - ask_exch1
    print ("Sell Exchange1 Buy Exchange2 - Spread:", spread2)

    # ===== Arbitrage condition and calculation =====
    if (spread1 > spread2) and spread1 > reqd_spread * (bid_exch1 + ask_exch1)/2:
        buy_order_price = exchange2.create_market_buy_order(symbol,
                                                            order_qty,
                                                            {'trading_agreement': 'agree'})
        sell_order_price = exchange1.create_market_sell_order(symbol,
                                                              order_qty,
                                                              {'trading_agreement': 'agree'})
        # buy_order_price = ask_exch2
        # sell_order_price = bid_exch1

    elif (spread2 > spread1) and spread2 > reqd_spread * (bid_exch2 + ask_exch2)/2:
        buy_order_price = exchange1.create_market_buy_order(symbol,
                                                            order_qty,
                                                            {'trading_agreement': 'agree'})
        sell_order_price = exchange2.create_market_sell_order(symbol,
                                                              order_qty,
                                                              {'trading_agreement': 'agree'})
        # buy_order_price = ask_exch1
        # sell_order_price = bid_exch2

    captured_spread = sell_order_price - buy_order_price

    print('Buy Order Price:',buy_order_price)
    print('Sell Order Price:', sell_order_price)


    return buy_order_price, sell_order_price, captured_spread


def check_openorders(symbol):
    if exchange1.fetch_open_orders(symbol) == True:
        try:
            exchange1.cancel_order()
        except: 'NetworkError'


# =============== **** Incomplete ****==============
# ***************************************************


# ======== Details of Open & Closed Trades =========
def trade_details(symbol):
    print("Closed Orders:")
    pprint.pprint(exchange1.fetch_closed_orders(symbol))
    pprint.pprint(exchange2.fetch_closed_orders(symbol))

    print("Open Orders:")
    pprint.pprint(exchange1.fetch_open_orders(symbol))
    pprint.pprint(exchange2.fetch_open_orders(symbol))

    print("My Trades:")
    pprint.pprint(exchange1.fetch_my_trades(symbol))
    pprint.pprint(exchange1.fetch_my_trades(symbol))


if __name__ == "__main__":
    run()





