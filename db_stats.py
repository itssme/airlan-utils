from typing import Tuple, List
from utils import db_models
from utils.stat_events import Events


def count_event_type(event: Events) -> int:
    return db_models.Stats.select().where(db_models.Stats.type == event.value).count()


def player_with_most(event: Events) -> List[Tuple[str, int]]:
    cursor = db_models.database.execute_sql(
        "select player.name, count(*) from stats join player on stats.player = player.id where stats.type = %s group by player.name order by count(*) desc, player.name limit 5",
        (event.value,))
    result: List[Tuple[str, int]] = list(cursor.fetchall())
    return result
