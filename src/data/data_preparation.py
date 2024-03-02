
class DataPreparation:
    """
    Responsável por preparar os dados para análise.
    """
    @staticmethod
    def calculate_adaptive_parameters(data, future_periods):
        total_days = (data['ds'].max() - data['ds'].min()).days
        initial_proportion = 0.5
        initial_days = max(365, int(total_days * initial_proportion))
        horizon_days = min(future_periods, total_days - initial_days - 90)
        period_days = max(30, int(horizon_days / 3))
        return f"{initial_days} days", f"{period_days} days", f"{horizon_days} days"
