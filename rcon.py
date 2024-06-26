import json
import logging
import os
from typing import Dict

from srcds.rcon import RconConnection


class RCON(RconConnection):
    def __init__(self, server, port=27015, password=os.getenv("RCON_PASSWORD", "pass"), single_packet_mode=True):
        super().__init__(str(server), port=port, password=password, single_packet_mode=single_packet_mode)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._sock.close()


def get5_status(server_ip: str, server_port: int) -> Dict:
    with RCON(server_ip, server_port) as rconn:
        get5_stats: str = rconn.exec_command("get5_status").decode("utf-8")
        get5_stats = get5_stats[get5_stats.find("{"):(get5_stats.rfind("}") + 1)].replace("\\n", "")
        logging.info("Get5 stats: " + get5_stats)
        get5_stats: Dict = json.loads(get5_stats)
        return get5_stats
