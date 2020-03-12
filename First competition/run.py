# Martingale

import sys
import time
import shift
import datetime as dt


def show(trader: shift.Trader):
    """
    This method provides information on the structure of PortfolioSummary and PortfolioItem objects:
     get_portfolio_summary() returns a PortfolioSummary object with the following data:
     1. Total Buying Power (get_total_bp())
     2. Total Shares (get_total_shares())
     3. Total Realized Profit/Loss (get_total_realized_pl())
     4. Timestamp of Last Update (get_timestamp())

     get_portfolio_items() returns a dictionary with "symbol" as keys and PortfolioItem as values,
     with each providing the following information:
     1. Symbol (get_symbol())
     2. Shares (get_shares())
     3. Price (get_price())
     4. Realized Profit/Loss (get_realized_pl())
     5. Timestamp of Last Update (get_timestamp())
    :param trader:
    :return:
    """

    print("Buying Power\tTotal Shares\tTotal P&L\tTimestamp")
    print(
        "%12.2f\t%12d\t%9.2f\t%26s"
        % (
            trader.get_portfolio_summary().get_total_bp(),
            trader.get_portfolio_summary().get_total_shares(),
            trader.get_portfolio_summary().get_total_realized_pl(),
            trader.get_portfolio_summary().get_timestamp(),
        )
    )

    print()

    print("Symbol\t\tShares\t\tPrice\t\t  P&L\tTimestamp")
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
    stop_time = dt.time(9, 51, 00) # todo delete

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


    # Show
    show(trader) # todo delete

    # disconnect
    trader.disconnect()

    return


if __name__ == "__main__":
    main(sys.argv)
