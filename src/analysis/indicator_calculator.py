class IndicatorCalculator:
    @staticmethod
    def calculate_RSI(data, column='Close', period=14):
        delta = data[column].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gains = gains.rolling(window=period, min_periods=1).mean()
        avg_losses = losses.rolling(window=period, min_periods=1).mean()
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        data['RSI'] = rsi
        return data

    @staticmethod
    def calculate_EMA(data, column='Close', period=21):
        ema = data[column].ewm(span=period, adjust=False).mean()
        data[f'EMA_{period}'] = ema
        return data

    @staticmethod
    def calculate_HiLo(data, period=14):
        high_column, low_column = 'High', 'Low'
        data['HiLo_High'] = data[high_column].rolling(window=period).max()
        data['HiLo_Low'] = data[low_column].rolling(window=period).min()
        return data
