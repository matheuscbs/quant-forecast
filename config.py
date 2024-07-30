import logging
import os

# Lista de tickers a serem processados
# tickers = ['SUZB3', 'KLBN3', 'CRFB3', 'BPAC3', 'GFSA3', 'SAPR4', 'BMEB4', 'CMIG4', 'AURE3', 'EUCA4', 'MGLU3', 'AGRO3', 'ROMI3', 'JHSF3', 'FESA4', 'COCE5', 'JBSS3', 'BMGB4', 'BHIA3', 'VIVT3', 'TASA4', 'PCAR3', 'ASAI3', 'TAEE11', 'LREN3', 'MRVE3', 'ITUB4', 'ITSA4', 'WEGE3', 'PETR4', 'VALE3', 'BBAS3', 'BRAP4', 'CMIN3', 'CSNA3', 'USIM5']
# tickers = ['PRIO3', 'RRRP3', 'PETR4', 'VALE3', 'BRAP4']
tickers = ['KLBN11']
# tickers = ['BTC/USDT']

# Variável para armazenar o ticker atual sendo processado
CURRENT_TICKER = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "..", "relatorios")
BASE_DIR = os.getenv("INVESTMENT_REPORTS_DIR", DEFAULT_REPORT_DIR)
REPORT_PATH = os.path.join(BASE_DIR, "relatorios")
IMAGE_PATH = os.path.join(REPORT_PATH, "images")

# Cria os diretórios se eles não existirem
try:
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(REPORT_PATH, exist_ok=True)
    os.makedirs(IMAGE_PATH, exist_ok=True)
except OSError as e:
    logging.error(f"Erro ao criar diretórios: {e}")
    raise

# Configurações padrão para busca de dados
DEFAULT_PERIOD = '3y'
DEFAULT_LAST_DAYS = 30
DEFAULT_FUTURE_PERIODS = 15
INTRADAY_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '90m', '1d']
DEFAULT_INTERVAL = '1h'

# Configurações para otimização de hiperparâmetros
N_TRIALS = 1
N_JOBS = 10

# URI para conexão com o banco de dados MongoDB (se aplicável)
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/investimentos_db')

# Função para iterar sobre os tickers e adicionar o sufixo ".SA"
def set_next_ticker():
    global CURRENT_TICKER
    for ticker in tickers:
        CURRENT_TICKER = ticker + ".SA"
        yield CURRENT_TICKER
