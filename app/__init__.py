from .git_utils import GitServices
from .boosters import Boosters
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a logging format
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s - %(name)s]: %(module)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
