import logging
import os

import config
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReportBuilder
from src.utils.file_manager import FileManager

from .analysis_utils import (AnalysisGenerator, generate_indicator_calculator,
                             generate_prophet_analysis,
                             generate_strategy_evaluator,
                             generate_volatility_analysis)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, data, client, ticker, period=config.DEFAULT_PERIOD, last_days=config.DEFAULT_LAST_DAYS, future_periods=config.DEFAULT_FUTURE_PERIODS, report_path=config.REPORT_PATH):
        self.data = data
        self.ticker = FileManager.normalize_ticker_name(ticker)
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.report_path = report_path
        self.image_paths = []
        self.plotter = Plotter(ticker, last_days, future_periods)
        report_file_path = os.path.join(report_path, f"{self.ticker}_report.pdf")
        FileManager.ensure_directory_exists(os.path.dirname(report_file_path))
        FileManager.ensure_directory_exists(self.report_path)
        self.builder = PDFReportBuilder(report_file_path)
        self.client = client

    def generate_report(self):
        logging.info("Iniciando a geração do relatório")
        analysis_functions = [
            AnalysisGenerator(
                generate_prophet_analysis,
                ['plotter', 'ticker', 'data', 'future_periods', 'client'],
                'Forecast de Séries Temporais',
                "Forecast de Séries Temporais"
            ),
            AnalysisGenerator(
                generate_indicator_calculator,
                ['plotter', 'data'],
                'Análise Estatística',
                "Análises com RSI, EMA, e HiLo indicators."
            ),
            AnalysisGenerator(
                generate_strategy_evaluator,
                ['plotter', 'ticker', 'data'],
                'Avaliação da Estratégia HiLo Activator',
                "Avaliação da performance da estratégia HiLo Activator."
            ),
            AnalysisGenerator(
                generate_volatility_analysis,
                ['plotter', 'data'],
                'Análise de Volatilidade',
                "Análise da volatilidade dos retornos utilizando modelos GARCH."
            )
        ]

        titles, descriptions, image_paths = [], [], []
        for analysis_function in analysis_functions:
            title, description, filenames = analysis_function.generate(
                plotter=self.plotter,
                ticker=self.ticker,
                data=self.data,
                future_periods=self.future_periods,
                client=self.client
            )
            if title and description and filenames:
                titles.append(title)
                descriptions.append(description)
                image_paths.append(filenames)
                self.image_paths.extend(filenames)

        if titles and descriptions and image_paths:
            self.builder.build(self.ticker, titles, descriptions, image_paths)
        else:
            logging.error("No valid information found to include in the report")

        logging.info("Geração do relatório concluída")

    def clean_up_files(self):
        logging.info("Iniciando a limpeza dos arquivos temporários")
        for path in self.image_paths:
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    logging.info(f"Arquivo {path} removido com sucesso.")
                except OSError as e:
                    logging.error(f"Erro ao remover arquivo {path}: {e}")
            else:
                logging.warning(f"Arquivo não encontrado: {path}")
