import logging
import sys

from watten2.server import Server
from watten2.network import GameMaster

format_msg: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s] => %(message)s"
format_date: str = "%m-%d-%Y %H:%M:%S"
level: int = logging.NOTSET

logger = logging.getLogger("GameMaster")
logging.basicConfig(format=format_msg, datefmt=format_date, level=level, stream=sys.stdout)


gm = GameMaster(logger=logger)
gm.allow_clients_to_join()

gm.server.close()

# serv = Server()
# serv.run()

