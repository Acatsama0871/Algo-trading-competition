import shift
import random
import time
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint


# Single order functions
# Market order
def market_order(trader: shift.Trader, order_type="Buy", symbols="AAPL", shares=1, wait=True): # todo error
    # Determine direction
    if order_type == "Buy":
        order = shift.Order(shift.Order.Type.MARKET_BUY, symbols, shares)
        order_id = order.id
    elif order_type == "Sell":
        order = shift.Order(shift.Order.Type.MARKET_SELL, symbols, shares)
        order_id = order.id

    # Submit order
    trader.submit_order(order)

    # If choose to wait for the order got executed
    if wait:
        while True:
            time.sleep(0.1)
            the_status = trader.get_order(order_id).status
            if the_status == shift.Order.Status.FILLED:
                break
        return order_id, trader.get_order(order_id).executed_price

    return order_id


# Multiple order functions
# Close-out, single symbol
def closeout(trader: shift.Trader, symbols):
    for i in symbols:
        try:
            NumberOfSize = int(trader.get_portfolio_items()[i].get_shares() / 100)

            if NumberOfSize > 0:
                market_sell = shift.Order(shift.Order.Type.MARKET_SELL, i, NumberOfSize)
                trader.submit_order(market_sell)
            elif NumberOfSize < 0:
                market_buy = shift.Order(shift.Order.Type.MARKET_BUY, i, -NumberOfSize)
                trader.submit_order(market_buy)
            elif NumberOfSize == 0:
                pass
        except KeyError:
            pass

    while True:
        time.sleep(0.1)
        size_sum = 0
        for i in trader.get_waiting_list():
            size_sum += i.size
        if size_sum == 0:
            break
    return


# Random buy or sell
def random_Buy_Sell(trader: shift.Trader, trader_side="Buy", symbol_list=["AAPL"], action_range=(1, 10), seed=1):
    for i in symbol_list:
        size = random.randint(action_range[0], action_range[1])  # Random size

        if trader_side == "Buy":
            market_order = shift.Order(shift.Order.Type.MARKET_BUY, i, size)
            trader.submit_order(market_order)
        elif trader_side == "Sell":
            market_order = shift.Order(shift.Order.Type.MARKET_SELL, i, size)
            trader.submit_order(market_order)
        else:
            return False
    return True


# Show functions
# Show the portfolio summary
def show_portfolio(trader: shift.Trader):
    print("Portfolio summary: ")
    print("Buying Power\tVolumes\t\tTotal P&L\tTimestamp")
    print(
        "%12.2f\t%9d\t%9.2f\t%26s"
        % (
            trader.get_portfolio_summary().get_total_bp(),
            trader.get_portfolio_summary().get_total_shares(),
            trader.get_portfolio_summary().get_total_realized_pl(),
            trader.get_portfolio_summary().get_timestamp(),
        )
    )

    print()

    print("Symbol\t\tShares\t\tPrice\t\tP&L\tTimestamp")
    for item in trader.get_portfolio_items().values():
        print(
            "%6s\t\t%6d\t%9.2f\t%9.2f\t%26s"
            % (
                item.get_symbol(),
                item.get_shares(),
                item.get_price(),
                item.get_realized_pl(),
                item.get_timestamp(),
            )
        )

    return


# Show the single order, according to id
def show_order(trader: shift.Trader, order_id):
    the_order = trader.get_order(order_id)
    # formatter = "{:6s}\t{:16s}\t{:7.2f}\t\t{:4d}\t{:36s}\t{:23s}\t\t{:26s}"
    formatter = "%6s\t%16s\t%7.2f\t\t%4d\t\t%4d\t\t%36s\t%23s\t\t%26s"
    print("Order: ")
    print("Symbol\t Type\t\t\t Price\t\t Size\t\tExecuted\tID\t\t\t\t\t\t Status\t\t\tTimestamp")
    print(formatter %(
        the_order.symbol,
        the_order.type,
        the_order.executed_price,
        the_order.size,
        the_order.executed_size,
        the_order.id,
        the_order.status,
        the_order.timestamp))

    return


# Statistics
# Sample price, single symbol
def get_sample_prices(trader: shift.Trader, symbols=["AAPL"], nums=1, delay=0.1, num_py=True):
    # Sample data
    result = []
    for i in range(1, nums + 1):
        time.sleep(delay)
        temp = []
        for j in symbols:
            while True:
                cur_price = trader.get_last_price(j)
                if cur_price != 0.0:
                    temp.append(trader.get_last_price(j))
                    break
        result.append(temp)

    # Arrange result
    result_ = []
    for i in range(0, len(symbols)):
        temp = []
        for j in range(0, nums):
            temp.append(result[j][i])
        result_.append(temp)

    if not num_py:
        return result_
    elif num_py:
        return np.array(result_)


# Con-integration p-value matrix
def conint_pvalues_matrix(prices_matrix):
    n = len(prices_matrix)
    result_matrix = np.empty(shape=(n, n))
    for i in range(0, n):
        for j in range(0, n):
            result_matrix[i][j] = coint(prices_matrix[i], prices_matrix[j])[1]

    return result_matrix

