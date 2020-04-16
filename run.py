import SHIFT_utilities as shift_u
import shift
import sys
import time
import numpy as np
import datetime as dt
import Stationary



def main(argv):
    # create trader object
    trader = shift.Trader("acatsama")

    # connect and subscribe to all available order books
    try:
        trader.connect("initiator.cfg", "cLbWKQzpWb9235NC")
        trader.sub_all_order_book()
    except shift.IncorrectPasswordError as e:
        print(e)
    except shift.ConnectionTimeoutError as e:
        print(e)

    # Wait market open
    time.sleep(300)

    # Set parameters
    observing_symbols = ["MSFT", "MMM", "AAPL", "INTC"]
    observing_delay = 4
    observing_num = 20 # extended
    significance_level = 0.1
    stationary_maintain = dt.timedelta(seconds=5) # reduced
    sd_width_1 = 1
    sd_width_2 = 7
    tolerance_level = 0.05
    buy_sell_timeDelta = 1 # extended
    sell_buy_shares = 1

    stop_time = dt.time(15, 30, 44)
    current_time = trader.get_last_trade_time().time()

    while current_time <= stop_time:

        observing_symbols = np.array(observing_symbols)

        # Sample data
        sample_result = shift_u.get_sample_prices(trader,
                                                  symbols=observing_symbols,
                                                  nums=observing_num,
                                                  delay=observing_delay)
        time.sleep(1)

        # Stationary test
        test_result = Stationary.stationary_test(sample_result, significance_level)
        trading_symbols = observing_symbols[test_result]
        trading_mean = Stationary.sample_mean(sample_result)[test_result]
        trading_sd = Stationary.sample_sd(sample_result)[test_result]
        trading_bounds = Stationary.trading_width(trading_mean, trading_sd, sd_width_1, sd_width_2)
        trading_num = len(trading_symbols)
        cur_time = trader.get_last_trade_time()
        benchmark_time = cur_time + stationary_maintain


        # Construct portfolio
        while cur_time < benchmark_time and trading_num != 0:
            for i in range(0, trading_num):
                cur_price = trader.get_last_price(trading_symbols[i])
                if trading_bounds[i][3] <= cur_price <= trading_bounds[i][1]:
                    market_buy = shift.Order(shift.Order.Type.MARKET_BUY, trading_symbols[i], sell_buy_shares)
                    trader.submit_order(market_buy)
                    time.sleep(buy_sell_timeDelta)
                elif trading_bounds[i][0] <= cur_price <= trading_bounds[i][2]:
                    market_sell = shift.Order(shift.Order.Type.MARKET_SELL, trading_symbols[i], sell_buy_shares)
                    trader.submit_order(market_sell)
                    time.sleep(buy_sell_timeDelta)
            cur_time = trader.get_last_trade_time()


        # Close out
        while True:
            delete_index = []
            for i in range(0, trading_num):
                cur_price = trader.get_last_price(trading_symbols[i])

                if abs(cur_price - trading_mean[i]) <= tolerance_level or cur_price >= trading_bounds[i][2] or cur_price <= trading_bounds[i][3]:
                    shift_u.closeout(trader, [trading_symbols[i]])
                    delete_index.append(i)
                time.sleep(1)

            if len(delete_index) != 0:
                trading_symbols = np.delete(trading_symbols, delete_index)
                trading_mean = np.delete(trading_mean, delete_index)
                trading_bounds = np.delete(trading_bounds, delete_index, 0)
                trading_sd = np.delete(trading_sd, delete_index)
                trading_num = len(trading_symbols)

            time.sleep(0.5)
            if trading_num == 0:
                break


        # Update stop condition
        current_time = trader.get_last_trade_time().time()


    # disconnect
    trader.disconnect()

    return


if __name__ == "__main__":
    main(sys.argv)
