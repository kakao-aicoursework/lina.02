import logging
from api import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-16s %(levelname)-8s %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.FileHandler('./server.log')


# uvicorn main:app --reload --host=0.0.0.0 --port=8000
if __name__ == "__main__":
    pass

