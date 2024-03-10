import logging
import os

from reportlab.lib.units import inch
from src.analysis.indicator_calculator import IndicatorCalculator
from src.analysis.prophet_analysis import ProphetAnalysis
from src.analysis.strategy_evaluator import StrategyEvaluator
from src.analysis.volatility_analysis import VolatilityAnalysis
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReportBuilder, PDFReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, ticker, data, period='5y', last_days=30, future_periods=15, report_path=None):
        self.ticker = ticker
        self.data = data
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.descriptions = {}
        self.titles = []
        self.filenames = []
        self.plotter = Plotter(ticker, last_days, future_periods)
        self.report_path = report_path
        self.builder = PDFReportBuilder(report_path, self.plotter.image_path)

    def generate_report(self):
        logging.info("Iniciando a geração do relatório")
        self.generate_indicator_calculator()
        self.generate_prophet_analysis()
        self.generate_strategy_evaluator()
        self.generate_volatility_analysis()
        self.builder.build(self.ticker, self.titles, list(self.descriptions.values()), self.filenames)
        logging.info("Geração do relatório concluída")

    def generate_prophet_analysis(self):
        logging.info("Gerando análise do Prophet")
        prophet = ProphetAnalysis(self.ticker, self.data, self.future_periods)
        model, forecast, df_cv = prophet.analyze()

        if model is not None and forecast is not None:

            self.descriptions['Prophet'] = "Análise de Séries Temporais com Prophet"
            self.titles.append('Análise de Séries Temporais com Prophet')

            prophet_forecast = self.plotter.plot_prophet_forecast(self.ticker, model, forecast)
            components = self.plotter.plot_components(self.ticker, model, forecast)
            metric = self.plotter.plot_cross_validation_metric(df_cv, "mape", "MAPE Metric", self.ticker)
            last_days = self.plotter.plot_last_days_forecast(self.data, forecast, self.future_periods, self.ticker, self.last_days)

            self.filenames.extend([last_days, components, prophet_forecast, metric])
        else:
            logging.error("Failed to generate Prophet analysis.")

    def generate_indicator_calculator(self):
        logging.info("Generating statistical analysis")
        self.data = IndicatorCalculator.calculate_RSI(self.data, 'Close')
        self.data = IndicatorCalculator.calculate_EMA(self.data, 'Close')
        self.data = IndicatorCalculator.calculate_HiLo(self.data, 'High', 'Low')

        self.descriptions['Indicator Calculator'] = "Analysis with RSI, EMA, and HiLo indicators."
        self.titles.append('Análise Estatística')

        indicators = self.plotter.plot_with_indicators(self.data, self.last_days)
        self.filenames.append(indicators)

    def generate_strategy_evaluator(self):
        logging.info("Generating strategy evaluation")
        price_data = self.data[['High', 'Low', 'Close']].copy()
        bounds = [(1, 100)]
        best_period, best_score = StrategyEvaluator.optimize_strategy(price_data, bounds)
        hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], int(best_period))

        if 'Date' not in price_data.columns:
            price_data['Date'] = price_data.index

        hilo_strategy = self.plotter.plot_hilo_strategy(price_data, best_period, self.ticker, hilo_long, hilo_short)
        self.filenames.append(hilo_strategy)

        description = f"Melhor período para HiLo Activator: {best_period} dias, Resultado da Estratégia: {best_score:.2f}"
        self.descriptions['Strategy Evaluation'] = description
        self.titles.append('Avaliação da Estratégia HiLo Activator')

    def generate_volatility_analysis(self):
        logging.info("Generating volatility analysis")
        volatility_analysis = VolatilityAnalysis(self.data['Retornos'])
        futura_volatilidade = volatility_analysis.analyze()
        garch = self.plotter.plot_garch_volatility(futura_volatilidade)
        self.filenames.extend([garch])
        last_volatility_value = futura_volatilidade.iloc[-1].item()
        self.descriptions['Volatility Analysis'] = f"Futura Volatilidade: {last_volatility_value:.2f}%"
        self.titles.append('Análise de Volatilidade')

    def clean_up_files(self):
        logging.info("Cleaning up generated files")
        for filename in self.filenames:
            filepath = os.path.join(self.plotter.image_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"Deleted file: {filename}")

    def __del__(self):
        try:
            self.clean_up_files()
        except AttributeError:
            pass
