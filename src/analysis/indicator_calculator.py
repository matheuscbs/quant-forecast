class IndicatorCalculator:
    @staticmethod
    def calculate_RSI(data, column='y', period=14):
        delta = data[column].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        data['RSI'] = rsi
        return data

    @staticmethod
    def calculate_EMA(data, column='y', period=21):
        ema = data[column].ewm(span=period, adjust=False).mean()
        data[f'EMA_{period}'] = ema
        return data

    @staticmethod
    def calculate_HiLo(data, high_column='High', low_column='Low', period=14):
        data['HiLo_High'] = data[high_column].rolling(window=period).max()
        data['HiLo_Low'] = data[low_column].rolling(window=period).min()
        return data
