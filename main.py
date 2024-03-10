from src.data.data_fetcher import YahooFinanceFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder

if __name__ == "__main__":
    ticker = 'WEGE3.SA'
    period = '5y'
    historical_period = 60
    future_period = 30

    data_fetcher = YahooFinanceFetcher()
    data = data_fetcher.fetch_data(ticker, period)

    if data is not None:
        report_generator = ReportGenerator(ticker, data)
        report_generator.generate_report()
        # report_generator.clean_up_files()
    else:
        print(f"Não foi possível buscar os dados para {ticker}.")
