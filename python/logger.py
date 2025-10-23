'''import logging as log
from logging.handlers import TimedRotatingFileHandler
import os
import datetime


LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


data_atual = datetime.datetime.now().strftime("%d-%m-%Y")
nome_arquivo = f"Log {data_atual}.log"
caminho_log = os.path.join(LOG_DIR, nome_arquivo)


# Cria um handler que troca o arquivo a cada dia (interval=1, when='midnight')
handler = TimedRotatingFileHandler(
    caminho_log,
    when="midnight",
    interval=1,
    backupCount=30,      # quantos arquivos antigos manter (opcional)
    encoding="utf-8"
)

# Formatter com data sem milissegundos
formatter = log.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"   # <-- sem milissegundos
)

handler.setFormatter(formatter)

# Configura o logger
logger = log.getLogger()
logger.setLevel(log.INFO)
logger.addHandler(handler)'''
