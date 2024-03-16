import config
from src.data.data_fetcher import YahooFinanceFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder

if __name__ == "__main__":
    data_fetcher = YahooFinanceFetcher()
    data = data_fetcher.fetch_data()
    print(data['ds'])
    if data is not None:
        report_generator = ReportGenerator(data)
        report_generator.generate_report()
        report_generator.clean_up_files()
    else:
        print(f"Não foi possível buscar os dados para {config.TICKER}.")
