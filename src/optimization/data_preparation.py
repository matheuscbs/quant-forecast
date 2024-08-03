import logging

import pandas as pd
from src.optimization.data_granularity_checker import DataGranularityChecker


class DataPreparation:
    @staticmethod
    def calculate_adaptive_parameters(data, future_periods, is_intraday):
        """Calcula parâmetros adaptativos para cross_validation do Prophet."""
        total_days = (data["ds"].max() - data["ds"].min()).days
        inferred_freq = pd.infer_freq(data["ds"])

        # Heurística para definir o período ideal
        period_map = {
            "T": pd.to_timedelta("1 days"),    # Minuto
            "H": pd.to_timedelta("1 days"),    # Hora
            "D": pd.to_timedelta("30 days"),   # Dia
            "W": pd.to_timedelta("90 days"),   # Semana
            "M": pd.to_timedelta("365 days"),  # Mês
        }

        if is_intraday:
            period = pd.to_timedelta("1 days")  # Força o período para 1 dia para dados intraday
        elif inferred_freq is not None and inferred_freq[0] in period_map:
            period = period_map[inferred_freq[0]]
        else:
            period = pd.to_timedelta(max(1, total_days // 20), unit='D')  # Estima o período com base no total de dias

        # Limites para horizonte e initial
        max_horizon = min(pd.to_timedelta(total_days * 0.2, unit='D'), period * 10)  # Máximo de 20% dos dados ou 10 períodos
        min_initial = max(period * 3, pd.to_timedelta(30, unit='D'))  # Mínimo de 3 períodos ou 30 dias

        # Ajuste do horizonte com base no future_periods e limites
        horizon = min(pd.to_timedelta(f"{future_periods} days"), max_horizon)

        # Cálculo do initial com base no horizonte e limites
        initial = max(pd.to_timedelta(total_days, unit='D') - horizon, min_initial)

        logging.info(f"Parâmetros adaptativos calculados: initial={initial}, period={period}, horizon={horizon}")
        return initial, period, horizon
