# Martingale

import sys
import time
import shift
import datetime as dt



def main(argv):
    # connect to shift
    trader = shift.Trader("acatsama")
    try:
        trader.connect("initiator.cfg", "cLbWKQzpWb9235NC")
        trader.sub_all_order_book()
    except shift.IncorrectPasswordError as e:
        print(e)
    except shift.ConnectionTimeoutError as e:
        print(e)

    # Wait for system start
    time.sleep(10)

    # Set stop time
    stop_time = dt.time(15, 30, 33)

    # Buy at the first time
    while True:
        time.sleep(0.5) # todo test
        aapl_market_buy = shift.Order(shift.Order.Type.MARKET_BUY, "AAPL", 10)
        trader.submit_order(aapl_market_buy)
        time.sleep(5) # todo test
        start_price = trader.get_portfolio_items()['AAPL'].get_price()
        buy_count = 1


        while True:
            # observe after 10 seconds
            time.sleep(5) # todo observe time
            current_price = trader.get_last_price("AAPL")
            time.sleep(0.05) # todo test
            # If current is larger than start_price: close out position
            if current_price > start_price or buy_count >= 17:
                sell_shares = int(trader.get_portfolio_items()["AAPL"].get_shares() / 100)
                while sell_shares > 0:
                    time.sleep(0.3) # todo test
                    aapl_market_sell_all = shift.Order(shift.Order.Type.MARKET_SELL, "AAPL", sell_shares)
                    trader.submit_order(aapl_market_sell_all)
                    time.sleep(0.8) # todo test
                    sell_shares = int(trader.get_portfolio_items()["AAPL"].get_shares() / 100)
                    time.sleep(5)
                break
            else:
                aapl_buy_more_shares = shift.Order(shift.Order.Type.MARKET_BUY, "AAPL", buy_count)
                trader.submit_order(aapl_buy_more_shares)
                time.sleep(0.05) # todo test
                buy_count += 1

        # access current time
        current_time = trader.get_last_trade_time().time()

        if current_time > stop_time:
            break


    # disconnect
    trader.disconnect()

    return


if __name__ == "__main__":
    main(sys.argv)
