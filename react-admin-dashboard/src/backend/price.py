import yfinance as yf
# import pandas as pd


dat = yf.download("CL=F", auto_adjust=False, interval='1mo')

filename = "real_time_oil_prices.csv"
dat.to_csv(path_or_buf=filename)
