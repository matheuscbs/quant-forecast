import pandas as pd


class DataGranularityChecker:
    @staticmethod
    def is_intraday(data):
        if not data.empty and 'ds' in data:
            time_diff = data['ds'].diff().min()
            return time_diff < pd.Timedelta(days=1)
        return False
