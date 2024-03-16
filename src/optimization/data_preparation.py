from src.optimization.data_granularity_checker import DataGranularityChecker


class DataPreparation:
    @staticmethod
    def calculate_adaptive_parameters(data, future_periods, is_intraday):
        total_days = (data['ds'].max() - data['ds'].min()).days

        if is_intraday:
            total_hours = total_days * 24
            horizon_hours = min(future_periods, total_hours - 48)
            initial_hours = int(0.75 * total_hours - horizon_hours)
            period_hours = max(24, int(horizon_hours / 3))

            initial_str = f"{initial_hours} hours"
            period_str = f"{period_hours} hours"
            horizon_str = f"{horizon_hours} hours"

        else:
            initial_proportion = 0.5
            horizon_days = min(future_periods, total_days - int(total_days * initial_proportion) - 30)
            initial_days = max(365, int(total_days * initial_proportion))
            period_days = max(30, int(horizon_days / 3))

            initial_str = f"{initial_days} days"
            period_str = f"{period_days} days"
            horizon_str = f"{horizon_days} days"

        return initial_str, period_str, horizon_str
