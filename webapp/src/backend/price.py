import yfinance as yf
import os
import pandas as pd


filename = os.path.join("data", "real_time_oil_prices.csv")


def get_price():
    try:
        dat = yf.download("CL=F", auto_adjust=False, interval='1mo')

        dat.to_csv(path_or_buf=filename)
        return

    except Exception as e:
        print(f"Error fetching real-time oil prices: {e}")
        return


def start():
    try:
        get_price()
        print("Saved prices to csv.")

    except Exception as e:
        print(f"Error while fetching prices: {e}")
