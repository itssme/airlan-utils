import logging
import os
import random
from typing import List, TypeVar, Generic, Dict, Optional, Tuple

import psycopg2
from fastapi import HTTPException, Depends
from peewee import fn, JOIN
from playhouse.shortcuts import model_to_dict

from utils import db_models
from utils.rabbitmq import EmailNotification, AdminMessage


async def reset_db_state():
    db_models.database._state._state.set(db_models.db_state_default.copy())
    db_models.database._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        db_models.database.connect()
        yield
    finally:
        if not db_models.database.is_closed():
            db_models.database.close()


def get_free_teams() -> List[db_models.Team]:
    all_teams = db_models.Team().select().where(db_models.Team.competing < 1)
    busy_teams = db_models.Team().select().join(db_models.Match, on=(
            (db_models.Team.id == db_models.Match.team1) | (db_models.Team.id == db_models.Match.team2))).where(
        db_models.Match.finished < 1)
    return list(all_teams - busy_teams)


def get_team_players(team_id: int) -> List[db_models.Player]:
    return list(db_models.Player().select().join(db_models.TeamAssignment,
                                                 on=(db_models.Player.id == db_models.TeamAssignment.player)).where(
        db_models.TeamAssignment.team == team_id))


def get_player_by_steam_id(steam_id: str) -> db_models.Player:
    return db_models.Player().select().where(db_models.Player.steam_id == steam_id).first()


def get_match_by_serverid(server_id: int) -> db_models.Match:
    return db_models.Match.select().join(db_models.Server, on=(db_models.Match.id == db_models.Server.match)).where(
        db_models.Server.id == server_id).first()


def get_server_for_match(matchid: str) -> db_models.Server:
    return db_models.Server.select().join(db_models.Match, on=(db_models.Server.match == db_models.Match.id)).where(
        db_models.Match.matchid == matchid).first()


def create_account(username: str, password: str):
    # TODO: refactor random string generation, create function and use better randomness (also see password reset token)
    account = db_models.Account.create(username=username, password=password, verification_code="".join(
        [random.choice([chr(random.randint(48, 57)), chr(random.randint(65, 90))]) for _ in range(0, 60)]))

    team = db_models.Team.create(name=f"{username}'s team", tag="tag", account=account,
                                 registration_fee_rnd="".join(
                                     [random.choice(
                                         [chr(random.randint(48, 57)), chr(random.randint(65, 90)),
                                          chr(random.randint(97, 122))]
                                     ) for _ in range(0, 10)]))

    try:
        EmailNotification().team_message(subject="Willkommen bei der airLAN",
                                         message=f"""Willkommen bei der airLAN. Damit sich euer Team auf der Anmeldeplattform einloggen kann, muss noch die E-Mail bestätigt werden: {os.getenv('WEB_SERVER_URL', 'https://airlan.comp-air.at')}/auth/verify/{account.verification_code}

Außerdem könnt ihr gerne auf den airLAN Discord kommen: https://discord.gg/r5WpnZa5UB""",
                                         team=team).send()
        AdminMessage(message=f"Neuer Account: {username}").send()
    except Exception as e:
        logging.error(f"Error sending email or admin message in account creation: {e}")
        team.delete()
        account.delete()
        raise HTTPException(status_code=500, detail="Account konnte nicht erstellt werden")


def get_team_id_by_account(username: str) -> Optional[int]:
    team = db_models.Team.get_or_none(db_models.Team.account == username)

    if team is None:
        return None
    else:
        return team.id


def get_team_registration_fee(team_id: int) -> float:
    base = int(db_models.Config.get(db_models.Config.key == "registration_fee_base_fee").value)
    food_orders = get_team_food_order_price(team_id)
    article_orders = get_team_article_order_price(team_id)
    return base + food_orders + article_orders


def get_team_food_order_price(team_id: int) -> float:
    return int(sum([food_type.price for food_type in db_models.FoodType.select().join(db_models.FoodOrder, on=(
            db_models.FoodType.id == db_models.FoodOrder.food)).join(db_models.TeamAssignment, on=(
            db_models.FoodOrder.player == db_models.TeamAssignment.player)).where(
        db_models.TeamAssignment.team == team_id)]))


def get_team_article_order_price(team_id: int) -> float:
    price_sum = (db_models.Team
                 .select(db_models.Team.id,
                         fn.SUM(db_models.ArticleType.price * db_models.ArticleOrder.quantity).alias("price_sum"))
                 .join(db_models.ArticleOrder, on=(db_models.Team.id == db_models.ArticleOrder.team))
                 .join(db_models.ArticleType, on=(db_models.ArticleOrder.article == db_models.ArticleType.id))
                 .group_by(db_models.Team.id).where(db_models.Team.id == team_id)).get_or_none()

    if price_sum is None:
        return 0
    return price_sum.price_sum


def get_order_details(user: db_models.Account) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
    team = model_to_dict(db_models.Team.get(db_models.Team.id == get_team_id_by_account(user.username)),
                         recurse=False)
    team["pizza_price"] = get_team_food_order_price(team["id"])
    team["article_price"] = get_team_article_order_price(team["id"])
    team["registration_fee"] = get_team_registration_fee(team["id"])

    food_orders = db_models.FoodType.select().join(db_models.FoodOrder,
                                                   on=(db_models.FoodOrder.food == db_models.FoodType.id)).join(
        db_models.Player, on=(db_models.Player.id == db_models.FoodOrder.player)).join(db_models.TeamAssignment,
                                                                                       on=(
                                                                                               db_models.TeamAssignment.player == db_models.Player.id)).where(
        db_models.TeamAssignment.team == team["id"]).where(db_models.FoodType.id != 1)

    food_types = db_models.FoodType.select().order_by(
        db_models.FoodType.id)

    article_orders = (db_models.ArticleType
                      .select(db_models.ArticleType.name, db_models.ArticleType.price,
                              db_models.ArticleOrder.quantity)
                      .join(db_models.ArticleOrder, on=(db_models.ArticleOrder.article == db_models.ArticleType.id))
                      .join(db_models.Team, on=(db_models.ArticleOrder.team == db_models.Team.id))
                      .where(db_models.Team.id == team["id"]))

    article_types = (db_models.ArticleType
                     .select(db_models.ArticleType.id, db_models.ArticleType.name,
                             db_models.ArticleType.description, db_models.ArticleType.image,
                             db_models.ArticleType.available_quantity,
                             (db_models.ArticleOrder.quantity * 1).alias("quantity"),  # wtf, peewee?
                             (db_models.ArticleOrder.quantity * db_models.ArticleType.price).alias("total_price"))
                     .join(db_models.ArticleOrder, JOIN.LEFT_OUTER, on=(
            (db_models.ArticleType.id == db_models.ArticleOrder.article_id) & (
            db_models.ArticleOrder.team == team["id"])))
                     .order_by(db_models.ArticleType.id))

    return team, food_orders, food_types, article_orders, article_types


def get_todos(username: str) -> List[Dict]:
    team_id = get_team_id_by_account(username)

    if team_id is None:
        return []

    team: db_models.Team = db_models.Team.get(db_models.Team.id == team_id)
    players = get_team_players(team_id)

    team_name_completed = team.name != f"{username}'s team" and team.tag != "tag"
    player_locked = not team_name_completed

    player_completed = len(players) == 5
    verify_locked = not player_completed
    registration_locked = team.verified != 1

    registration_fee_completed = team.paid_registration_fee
    if team.sponsored:
        registration_fee_completed = True

    verified_teams = db_models.Team.select().where(db_models.Team.verified == 1).count()
    max_teams = int(db_models.Config.get(db_models.Config.key == "max_teams").value)

    return [
        {  # registration
            "completed": True,
            "title": "Registrieren",
            "desc": "Registriere dich auf dieser Plattform."
        },
        {  # team name
            "completed": team_name_completed,
            "title": "Team Namen Angeben",
            "desc": "Gib den Namen und den Tag deines Teams an.",
            "route": "/public/team/registration",
            "display_only": team.locked_changes == 1
        },
        {  # player
            "completed": player_completed,
            "title": "Spieler Hinzufügen",
            "desc": "Füge alle fünf Spieler zu deinem Team hinzu.",
            "route": "/public/team/add_members",
            "locked": player_locked,
            "display_only": team.locked_changes == 1
        },
        {  # verified
            "substep": team.locked_changes == 1,
            "completed": team.verified == 1,
            "title": "Daten Bestätigt",
            "route": "/public/team/confirm_data",
            "desc": f"Bestätige deine Daten und Warte bis die Veranstalter sie nochmals geprüft haben und dich zum Turnier freischalten. Plätze: {verified_teams}/{max_teams}",
            "locked": verify_locked,
            "display_only": team.locked_changes == 1
        },
        {  # paid registration fee
            "completed": registration_fee_completed,
            "title": "Teilnahmegebühr Zahlen",
            "desc": "Überweise die Teilnahmegebühr und warte auf die Bestätigung." if not team.sponsored else "Geponsortes team, keine Teilnahmegebühr fällig.",
            "route": "/public/team/fee",
            "locked": registration_locked
        }
    ]


def get_rules():
    rules = [
        {"id": 1, "rule": "Teams", "subrules":
            [
                "Ein Team besteht aus genau fünf Spielern.",
                "Ein Spieler kann nur in einem Team sein.",
                "Jedes Team hat einen Teamleiter. Dieser muss das Team auf dieser Plattform registrieren.",
                "Der Teamleader ist für das Auswählen der Karten während des Spiels verantwortlich.",
                "Im Tunier werden 12 Teams gegeneinandern antreten."
            ]
         },
        {"id": 2, "rule": "Finale", "subrules":
            [
                "Die besten zwei Teams (jene die Gewinner des Halbfinales aus Gruppe A) spielen im Finale gegeneinander.",
                "Das Finale wird ein Best-of-Three Match zwischen den beiden Teams sein, welches für alle anderen Tunierteilnehmer übertragen wird."
            ]
         },
        {"id": 3, "rule": "Spielmodus", "subrules":
            [
                "Das Turnier wird im 'jeder gegen jeden' Modus begonnen.",
                "In der zweiten Phase, werden die Teams in zwei Gruppen aufgeteilt, in denen sie jeweils gegen jedes andere Team in ihrer Gruppe spielen.",
                "In Gruppe A spielen die Teams, welche die meisten Punkte in der ersten Phase gesammelt haben. In Gruppe B spielen die Teams, welche die wenigsten Punkte in der ersten Phase gesammelt haben.",
                "Das Halbfinale wird zwischen den vier besten Teams aus Gruppe A gespielt (1. gegen 4. und 2. gegen 3.).",
                "Jedes Spiel wird in einem Best-of-One Modus gespielt. (Außer das Finale, welches im Best-of-Three Modus gespielt wird.)",
                "Die Karten werden vor dem Spiel in einem Veto System von den Teamleitern ausgewählt.",
                "Danach wird eine Knife Runde auf der Map gespielt. Der Gewinner der Knife Runde entscheidet, welche Seite er spielen möchte. (CT oder T)",
                "Alle Maps werden im Bomb-Defuse Modus gespielt, bis auf Office, welche im Hostage Modus gespielt wird.",
                # "Bei einem Unentschieden wird eine Overtime gespielt, bei der beide Teams im Spiel mit 10.000$ starten und sechs Runden spielen müssen.",
                # "Sollte es nach den sechsten Runden wieder ein Unentschieden geben, wird eine weitere Overtime gespielt, bei der wieder beide Teams im Spiel mit 10.000$ starten und 6 Runden spielen müssen."
            ]
         },
        {"id": 4, "rule": "Allgemeine Turnierregeln", "subrules":
            [
                "Die Regeln des Turniers werden auf dieser Plattform veröffentlicht und können jederzeit geändert werden.",
                "Alle Spiele werden aufgenommen und die Demo Dateien anschliessend veröffentlicht.",
                "Der Teamleiter hat all seine Spieler über die hier veröffentlichen Regeln zu Unterrichten. Unwissenheit über Regeln sind dem Team anzulasten.",
                "Teams, welche sich unsportliche Verhalten, oder andere Spieler oder Teams, in einer verletzenden Art und Weise beleidigen, welche selbst für den in CS2 herrschenden rauen Umgangston unüblich ist, können gewonnene Spiele gestrichen werden, oder in besonders schwerwiegenden Fällen vom Turnier ausgeschlossen.",
            ]
         },
        {"id": 5, "rule": "Turnierausschluss", "subrules":
            [
                "Alle Programme oder andere nicht technischen Hilfsmittel, welche einem Spieler, oder einem Team als ganzes, einen Vorteil gegenüber anderen Teams verschaffen, sind verboten. Ausgenommen sind Programme welche im allgemeinen Verständnis der cs2 Spieler nicht als Cheats angesehen werden, wie unter anderem Programme zur Kommunikation mit den anderen Spielern außerhalb des ingame-chats, wie Discord oder Teamspeak.",
                "Modifikationen, die innerhalb des CS2 Clients stattfinden, wie unter anderem Jump-Throw-Binds, sind erlaubt.",
                "Das Angreifen des Servers oder der Clients anderer Spieler ist verboten, dazu zählen insbesondere, DDOS Attacken oder ähnliches.",
                "Wenn ein Spieler des Teams gegen die Regeln des §5 verstößt, wird das gesamte Team disqualifiziert und der Spieler wird für alle zukünftigen Turniere gesperrt.",
            ]
         },
    ]
    return rules


def get_least_used_host_ips() -> str:
    cursor = db_models.database.execute_sql(
        "select host.ip from host left join server on host.ip = server.ip group by host.ip order by count(server.ip) asc")
    result: List[Tuple[str, int]] = list(cursor.fetchall())

    if len(result) == 0:
        logging.error("No available hosts found to host a game")
        raise ValueError("No available hosts found to host a game")

    logging.info(f"Least used host ips: {result}")

    return random.choice(result)[0]


def get_default_template_values() -> Dict:
    config: db_models.Config
    return {
        "config": {config.key: config.value for config in db_models.Config.select()}
    }
