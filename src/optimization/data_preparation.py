import pandas as pd
from src.optimization.data_granularity_checker import DataGranularityChecker


class DataPreparation:
    @staticmethod
    def calculate_adaptive_parameters(data, future_periods, is_intraday):
        """Calcula parâmetros adaptativos para cross_validation do Prophet."""
        total_days = (data["ds"].max() - data["ds"].min()).days

        inferred_freq = pd.infer_freq(data["ds"])
        if is_intraday:
            if inferred_freq is None:
                raise ValueError("Frequência dos dados não detectada para dados intraday")

            freq_unit = inferred_freq[0]

            # Períodos totais:
            period_to_days = {'T': 1 / (24 * 60), 'H': 1 / 24}
            total_periods = total_days / period_to_days.get(freq_unit, 1)

            max_horizon_periods = int(0.75 * total_periods)

            horizon_periods = min(
                future_periods * 60 if freq_unit == 'T' else future_periods,
                max_horizon_periods
            )

            # Initial:
            initial_periods = total_periods - horizon_periods - max(24 * 60 if freq_unit == 'T' else 48, horizon_periods)
            initial_periods = max(initial_periods, 24 * 60 if freq_unit == 'T' else 48)

            period_periods = min(initial_periods // 2, horizon_periods)

            initial_str = f"{initial_periods // 24}D" if initial_periods >= 24 else f"{initial_periods}H"
            period_str = f"{period_periods // 24}D" if period_periods >= 24 else f"{period_periods}H"
            horizon_str = f"{horizon_periods // 24}D" if horizon_periods >= 24 else f"{horizon_periods}H"
        else:
            initial_proportion = 0.8
            horizon_days = min(future_periods, int(total_days * (1 - initial_proportion)) - 30)
            initial_days = max(365, int(total_days * initial_proportion))
            period_days = max(30, horizon_days // 3)

            initial_str = f"{initial_days}D"
            period_str = f"{period_days}D"
            horizon_str = f"{horizon_days}D"

        return initial_str, period_str, horizon_str
