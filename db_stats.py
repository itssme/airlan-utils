import logging
import os
from typing import Tuple, List

import psycopg2

from utils.db import DbObjImpl, Stats
from utils.stat_events import Events


def count_event_type(event: Events) -> int:
    with psycopg2.connect(
            host=os.getenv("POSTGRES_DB_HOST", "db"),
            port=int(os.getenv('POSTGRES_DB_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv("POSTGRES_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select count(*) from stats where type = %s", (event.value,))
            return cursor.fetchall()[0][0]


def player_with_most(event: Events) -> List[Tuple[str, int]]:
    with psycopg2.connect(
            host=os.getenv("POSTGRES_DB_HOST", "db"),
            port=int(os.getenv('POSTGRES_DB_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv("POSTGRES_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "select player.name, count(*) from stats join player on stats.player = player.id where stats.type = %s group by player.name order by count(*) desc, player.name limit 5",
                (event.value,))
            result = cursor.fetchall()
            if len(result) == 0:
                return []
            return result
