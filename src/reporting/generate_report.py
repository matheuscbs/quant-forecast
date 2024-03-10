import logging
import os

import config
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReportBuilder

from .analysis_utils import (generate_indicator_calculator,
                             generate_prophet_analysis,
                             generate_strategy_evaluator,
                             generate_volatility_analysis)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, ticker, data, period=config.DEFAULT_PERIOD, last_days=config.DEFAULT_LAST_DAYS, future_periods=config.DEFAULT_FUTURE_PERIODS, report_path=config.REPORT_PATH):
        self.ticker = ticker
        self.data = data
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.report_path = report_path
        self.plotter = Plotter(ticker, last_days, future_periods)
        self.builder = PDFReportBuilder(os.path.join(report_path, f"{ticker}_report.pdf"))

    def generate_report(self):
        logging.info("Iniciando a geração do relatório")
        analysis_functions = [
            generate_prophet_analysis,
            generate_indicator_calculator,
            generate_strategy_evaluator,
            generate_volatility_analysis,
        ]

        titles, descriptions, image_paths = [], [], []
        for func in analysis_functions:
            title, description, filenames = func(
                plotter=self.plotter,
                ticker=self.ticker,
                data=self.data,
                future_periods=self.future_periods
            )
            if title and description and filenames:
                titles.append(title)
                descriptions.append(description)
                image_paths.append(filenames)

        if titles and descriptions and image_paths:
            self.builder.build(self.ticker, titles, descriptions, image_paths)
        else:
            logging.error("No valid information found to include in the report")

        logging.info("Geração do relatório concluída")

    def __del__(self):
        try:
            self.plotter.clean_up_files()
        except AttributeError:
            pass
