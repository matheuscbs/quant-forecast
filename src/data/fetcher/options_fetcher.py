import datetime as dt
import logging

import pandas as pd
import yfinance as yf


class OptionsFetcher:
    def __init__(self, ticker):
        self.ticker = ticker
        self.logger = logging.getLogger(__name__)

    def fetch_options_data(self):
        self.logger.info(f"Fetching options data for {self.ticker}...")
        try:
            tk = yf.Ticker(self.ticker)
            return tk
        except Exception as e:
            self.logger.error(f"Failed to fetch options data for {self.ticker}: {e}")
            return None

    def get_expiry_dates(self, ticker):
        try:
            expiry_dates = ticker.options
            return expiry_dates
        except Exception as e:
            self.logger.error(f"Failed to get expiry dates for {self.ticker}: {e}")
            return []

    def parse_options_data(self, ticker, expiry_date):
        try:
            options = ticker.option_chain(expiry_date)
            calls = options.calls
            puts = options.puts

            calls['optionType'] = 'C'
            puts['optionType'] = 'P'

            all_options = pd.concat(objs=[calls, puts], ignore_index=True)

            return all_options
        except Exception as e:
            self.logger.error(f"Failed to parse options data for {self.ticker}: {e}")
            return None
