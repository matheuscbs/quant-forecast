import logging
import signal
import time
import warnings

import config
from dask.distributed import Client
from src.data.fetcher.crypto_data_fetcher import CryptoDataFetcher
from src.data.fetcher.data_fetcher import YahooFinanceFetcher
from src.data.fetcher.options_fetcher import OptionsFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder


def signal_handler(signal, frame):
    logging.warning("KeyboardInterrupt detected, shutting down Dask client gracefully...")
    client.shutdown()
    exit(1)

warnings.filterwarnings("ignore", category=FutureWarning, module="prophet.plot")

def is_crypto(ticker):
    return "/" in ticker

def process_ticker(ticker, client):
    if is_crypto(ticker):
        data_fetcher = CryptoDataFetcher()
    else:
        data_fetcher = YahooFinanceFetcher()

    data = data_fetcher.fetch_data(ticker=ticker)

    if data is not None and not data.empty:
        print(f"Dados para {ticker}: ", data.columns)
        report_generator = ReportGenerator(data, ticker=ticker, client=client)
        report_generator.generate_report()
        report_generator.clean_up_files()
    else:
        print(f"Não foi possível buscar os dados para {ticker}.")

def fetch_and_process_options(tickers):
    for ticker in tickers:
        options_fetcher = OptionsFetcher(ticker)
        tk = options_fetcher.fetch_options_data()
        if tk:
            expiry_dates = options_fetcher.get_expiry_dates(tk)
            if expiry_dates:
                for exp_date in expiry_dates:
                    all_options = options_fetcher.parse_options_data(tk, exp_date)
                    if all_options is not None:
                        print(f"Opções para {ticker} na data de expiração {exp_date}:")
                        print(all_options)
                    else:
                        print(f"Failed to parse options data for {ticker} at expiration date {exp_date}.")
            else:
                print(f"Failed to fetch expiry dates for {ticker}.")
        else:
            print(f"Failed to fetch options data for {ticker}.")
        time.sleep(5)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # fetch_and_process_options(config.tickers)

    with Client() as client:
        for ticker in config.tickers:
            if is_crypto(ticker):
                process_ticker(ticker, client)
            else:
                for ticker in config.set_next_ticker():
                    process_ticker(ticker, client)
