import logging

import pandas as pd
from pandas.tseries.frequencies import to_offset


class DataGranularityChecker:
    @staticmethod
    def is_intraday(data):
        if not data.empty and 'ds' in data and not data['ds'].isnull().all():
            try:
                inferred_freq = pd.infer_freq(data['ds'])
                if not inferred_freq:
                    return False
                return to_offset(inferred_freq) < to_offset('D')
            except ValueError as e:
                logging.warning(f"Error inferring data frequency: {e}")
                return False
        return False
