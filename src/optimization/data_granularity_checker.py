import pandas as pd


class DataGranularityChecker:
    @staticmethod
    def is_intraday(data):
        if not data.empty and 'ds' in data:
            inferred_freq = pd.infer_freq(data['ds'])
            return inferred_freq and inferred_freq.startswith(('T', 'H', 'min', 'S'))
        return False
