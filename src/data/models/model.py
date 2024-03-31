from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (BooleanField, DateTimeField, DictField,
                                EmbeddedDocumentField,
                                EmbeddedDocumentListField, FloatField,
                                ListField, ReferenceField, StringField)


class Asset(Document):
    asset_type = StringField(required=True, choices=['Stock', 'Cryptocurrency'])
    ticker = StringField(required=True)
    name = StringField(required=True)
    sector = StringField()  # Opcional, principalmente para ações
    historical_data = ListField(ReferenceField('TimeSeries'))

class TimeSeries(Document):
    asset = ReferenceField('Asset', required=True)
    date = DateTimeField(required=True)
    open_price = FloatField(required=True)
    close_price = FloatField(required=True)
    high = FloatField(required=True)
    low = FloatField(required=True)
    volume = FloatField(required=True)

class ForecastInterval(EmbeddedDocument):
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)
    interval = StringField(required=True, choices=['1m', '5m', '15m', '30m', '1h', '90m', '1d'])

class Forecast(Document):
    asset = ReferenceField('Asset', required=True)
    model = ReferenceField('Model', required=True)
    forecast_period = EmbeddedDocumentField('ForecastInterval', required=True)
    forecast_data = EmbeddedDocumentListField('ForecastData')

class Model(Document):
    model_type = StringField(required=True, choices=['Prophet', 'LSTM', 'ARIMA'])
    parameters = DictField()  # Para armazenar parâmetros de forma estruturada
    training_date = DateTimeField(required=True)
    performance_metrics = DictField()  # Armazenar métricas como dicionário
    active = BooleanField(default=True)

class Report(Document):
    asset = ReferenceField('Asset', required=True)
    report_type = StringField(required=True, choices=['Technical Analysis', 'Forecast'])
    file_path = StringField(required=True)
    generation_date = DateTimeField(required=True)

class Configuration(Document):
    key = StringField(required=True, unique=True)
    value = StringField(required=True)
