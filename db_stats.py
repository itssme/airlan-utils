from typing import Tuple, List, Dict
from utils import db_models
from utils.stat_events import Events


def count_all_events() -> List[Tuple[int, int]]:
    cursor = db_models.database.execute_sql("select type, count(*) from stats group by type")
    result: List[Tuple[int, int]] = list(cursor.fetchall())
    return result


def count_event_type(event: Events) -> int:
    return db_models.Stats.select().where(db_models.Stats.type == event.value).count()


def player_with_most(event: Events) -> List[Tuple[str, int]]:
    cursor = db_models.database.execute_sql(
        "select player.name, count(*) from stats join player on stats.player = player.id where stats.type = %s group by player.name order by count(*) desc, player.name limit 5",
        (event.value,))
    result: List[Tuple[str, int]] = list(cursor.fetchall())
    return result
