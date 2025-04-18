# import yfinance as yf
# import os

import yfinance as yf
import os

def download_oil_prices(output_dir="data", filename="real_time_oil_prices.csv"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download oil price data
    dat = yf.download("CL=F", auto_adjust=False, interval='1mo')
    
    # Save to CSV
    filepath = os.path.join(output_dir, filename)
    dat.to_csv(path_or_buf=filepath)
    
    return filepath

if __name__ == "__main__":
    download_oil_prices()

    # old
    # dat = yf.download("CL=F", auto_adjust=False, interval='1mo')
    # filename = os.path.join("data", "real_time_oil_prices.csv")
    # dat.to_csv(path_or_buf=filename)
