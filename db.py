import logging
import os
import random
from typing import List, TypeVar, Generic, Dict, Optional

import psycopg2

from utils import db_models


class DbObject(object):
    def tuple(self):
        return tuple(vars(self).values())

    def to_json(self) -> dict:
        return vars(self)

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return str(self.to_json())

    def insert_into_db(self):
        with psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database="postgres",
                user="postgres",
                password=os.getenv("DB_PASSWORD", "pass")) as conn:
            with conn.cursor() as cursor:
                self.insert_into_db_with_cursor(cursor)

    def insert_into_db_with_cursor(self, cursor):
        stmt = f"insert into {self.__class__.__name__.lower()} ({', '.join(list(filter(lambda key: (key != 'id'), list(vars(self).keys()))))}) values ({', '.join(['%s' for elm in list(filter(lambda key: (key != 'id'), list(vars(self).keys())))])}) {'returning id' if 'id' in list(vars(self).keys()) else ''}"
        values = tuple(
            self.__getattribute__(elm) for elm in
            list(filter(lambda key: (key != 'id'), list(vars(self).keys()))))
        logging.info(f"Running query: {stmt}\nwith values: {values}")
        cursor.execute(stmt, values)
        if "id" in vars(self).keys():
            self.__setattr__("id", cursor.fetchall()[0][0])

    # WARNING: Currently only works if the object is using the 'id' attribute as primary key
    def update_attribute(self, attr: str):
        if "id" not in vars(self).keys():
            raise NotImplemented("Cannot insert object that does not use 'id' as primary key")

        with psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database="postgres",
                user="postgres",
                password=os.getenv("DB_PASSWORD", "pass")) as conn:
            with conn.cursor() as cursor:
                self.update_attribute_with_cursor(cursor, attr)

    def update_attribute_with_cursor(self, cursor, attr: str):
        stmt = f"update {self.__class__.__name__.lower()} set {attr} = %s where id = %s"
        values = (self.__getattribute__(attr), self.__getattribute__("id"))
        logging.info(f"Running query: {stmt}\nwith values: {values}")
        cursor.execute(stmt, values)


class Server(DbObject):
    def __init__(self, id: int = None, ip: str = "host.docker.internal", port: int = None, gslt_token: str = "",
                 container_name: str = None, match: int = None):
        self.id: int = id
        self.ip: str = ip
        self.port: int = port
        self.gslt_token: str = gslt_token
        self.container_name: str = container_name
        self.match: int = match


class Match(DbObject):
    def __init__(self, id: int = None, matchid: str = "", name: str = "", team1: int = None, team2: int = None,
                 best_out_of: int = None, number_in_map_series: int = 0, series_score_team1: int = 0,
                 series_score_team2: int = 0, finished: int = 0):
        self.id: int = id
        self.matchid: str = matchid
        self.name: str = name
        self.team1: int = team1
        self.team2: int = team2
        self.best_out_of: int = best_out_of
        self.number_in_map_series: int = number_in_map_series
        self.series_score_team1: int = series_score_team1
        self.series_score_team2: int = series_score_team2
        self.finished: int = finished


class Stats(DbObject):
    def __init__(self, id: int = None, match: int = None, player: int = None, type: int = None):
        self.id: int = id
        self.match: int = match
        self.player: int = player
        self.type: int = type


class Account(DbObject):
    def __init__(self, username: str = None, password: str = None, role: str = "user"):
        self.username: str = username
        self.password: str = password
        self.role: str = role


T = TypeVar("T", Server, Match, Stats, Account)


class DbObjImpl(Generic[T]):
    def from_json(self, dict: dict) -> T:
        obj = self.__orig_class__.__args__[0]()
        for attr in vars(obj).keys():
            if attr in dict.keys():
                obj.__setattr__(attr, dict[attr])

        return self.from_tuple(tuple(vars(obj).values()))

    def from_tuple(self, tuple: tuple) -> T:
        return self.__orig_class__.__args__[0](*tuple)


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


def get_servers() -> List[Server]:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from server")
            servers = cursor.fetchall()
            return [DbObjImpl[Server]().from_tuple(server) for server in servers]


def insert_server(server: Server):
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            server.insert_into_db_with_cursor(cursor)


def get_server_by_id(server_id: int) -> Server:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from server where id = %s", (server_id,))
            return DbObjImpl[Server]().from_tuple(cursor.fetchall()[0])


def delete_server(server_id: int):
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("delete from server where id = %s", (server_id,))


def get_matches() -> List[Match]:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from match")
            matches = cursor.fetchall()
            return [DbObjImpl[Match]().from_tuple(match) for match in matches]


def get_match_by_id(match_id: int) -> Match:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from match where id = %s", (match_id,))
            return DbObjImpl[Match]().from_tuple(cursor.fetchall()[0])


def get_match_by_matchid(matchid: str) -> Match:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from match where matchid = %s", (matchid,))
            return DbObjImpl[Match]().from_tuple(cursor.fetchall()[0])


def get_match_by_serverid(server_id: int) -> Match:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select match.* from match join server on server.match = match.id where server.id = %s",
                           (server_id,))
            return DbObjImpl[Match]().from_tuple(cursor.fetchall()[0])


def insert_match(match: Match):
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            match.insert_into_db_with_cursor(cursor)


def get_server_for_match(matchid: str) -> Server:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select server.* from server join match on server.match = match.id where match.matchid = %s",
                           (matchid,))
            return DbObjImpl[Server]().from_tuple(cursor.fetchall()[0])


def get_hosts() -> List[str]:
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from host")
            server_tuple_list = cursor.fetchall()
            return [host[0] for host in server_tuple_list]


def get_least_used_host_ips():
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "select host.* from host left join server on host.ip = server.ip group by host.ip order by count(server.ip) asc")
            host_list = cursor.fetchall()
            if len(host_list) == 0:
                logging.info(
                    f"get_least_used_host_ips: no hosts found -> inserting external ip or default value: {os.getenv('EXTERNAL_IP', 'host.docker.internal')}")
                insert_host(os.getenv("EXTERNAL_IP", "host.docker.internal"))
                return get_least_used_host_ips()

            logging.info(f"get_least_used_host_ips: {host_list}")
            return host_list[0][0]


def insert_host(host_ip: str):
    with psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASSWORD", "pass")) as conn:
        with conn.cursor() as cursor:
            cursor.execute("insert into host (ip) values (%s)", (host_ip,))


def create_account(username: str, password: str):
    account = db_models.Account.create(username=username, password=password)

    db_models.Team.create(name=f"{username}'s team", tag="tag", account=account,
                          registration_fee_rnd="".join(
                              [random.choice(
                                  [chr(random.randint(48, 57)), chr(random.randint(65, 90)),
                                   chr(random.randint(97, 122))]
                              ) for _ in range(0, 10)]))


def get_team_id_by_account(username: str) -> Optional[int]:
    team = db_models.Team.get_or_none(db_models.Team.account == username)

    if team is None:
        return None
    else:
        return team.id


def get_team_registration_fee(team_id: int) -> int:
    base = 50  # TODO: make configurable?
    orders = get_team_order_price(team_id)
    return base + orders


def get_team_order_price(team_id: int) -> int:
    return int(sum([food_type.price for food_type in db_models.FoodType.select().join(db_models.Order, on=(
            db_models.FoodType.id == db_models.Order.food)).join(db_models.TeamAssignment, on=(
            db_models.Order.player == db_models.TeamAssignment.player)).where(
        db_models.TeamAssignment.team == team_id)]))


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

    return [
        {  # registration
            "completed": True,
            "title": "Registrieren",
            "desc": "Registriere dich auf dieser Plattform."
        },
        {  # team name
            "completed": team_name_completed,
            "title": "Team Namen Angeben",
            "desc": "Gib den Namen und den Tag deinen Teams an.",
            "route": "/public/team/registration",
            "display_only": team.locked_changes
        },
        {  # player
            "completed": player_completed,
            "title": "Spieler Hinzufügen",
            "desc": "Füge alle fünf Spieler zu deinem Team hinzu.",
            "route": "/public/team/add_members",
            "locked": player_locked,
            "display_only": team.locked_changes
        },
        {  # verified
            "substep": team.locked_changes == 1,
            "completed": team.verified == 1,
            "title": "Daten Bestätigt",
            "route": "/public/team/confirm_data",
            "desc": f"Bestätige deine Daten und Warte bis die Veranstalter sie nochmals geprüft haben und dich zum Turnier freischalten. Plätze: {verified_teams}/10",
            "locked": verify_locked
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
                "Im Tunier werden zehn Teams gegeneinandern antreten."
            ]
         },
        {"id": 2, "rule": "ELO-System", "subrules":
            [
                "Jedes Team hat einen ELO-Wert, der die Stärke des Teams angibt. Alle Teams starten mit einem ELO Wert von 1000.",
                "Nach jedem Spiel wird der ELO-Wert des Teams angepasst. Dabei wird der ELO-Wert des Gegners berücksichtigt, sowie der Unterschied der Scores. (ähnlich wie bei der ELO-Ratingliste im Schach)"
            ]
         },
        {"id": 3, "rule": "Finale", "subrules":
            [
                "Die besten zwei Teams (jene mit der höchsten ELO) spielen im Finale gegeneinander.",
                "Das Finale wird ein normales Match zwischen den beiden Teams sein, welches für alle anderen Tunierteilnehmer übertragen wird."
            ]
         },
        {"id": 4, "rule": "Spielmodus", "subrules":
            [
                "Das Turnier wird im ELO-System begonnen.",
                "Jedes Spiel wird in einem Best-of-One Modus gespielt.",
                "Die Karten werden vor dem Spiel in einem Veto System von den Teamleitern ausgewählt.",
                "Danach wird eine Knife Runde auf der Map gespielt. Der Gewinner der Knife Runde entscheidet, welche Seite er spielen möchte. (CT oder T)",
                "Alle Maps werden im Bomb-Defuse Modus gespielt, bis auf Agency, welche im Hostage Modus gespielt wird.",
                "Bei einem Unentschieden wird eine Overtime gespielt, bei der beide Teams im Spiel mit 10.000$ starten und sechs Runden spielen müssen.",
                "Sollte es nach den sechsten Runden wieder ein Unentschieden geben, wird eine weitere Overtime gespielt, bei der wieder beide Teams im Spiel mit 10.000$ starten und 6 Runden spielen müssen."
            ]
         },
        {"id": 5, "rule": "Allgemeine Turnierregeln", "subrules":
            [
                "Die Regeln des Turniers werden auf dieser Plattform veröffentlicht und können jederzeit geändert werden.",
                "Alle Spiele werden aufgenommen und die Demo Dateien anschliessend veröffentlicht.",
                "Der Teamleiter hat all seine Spieler über die hier veröffentlichen Regeln zu Unterrichten. Unwissenheit über Regeln sind dem Team anzulasten.",
                "Teams, welche sich unsportliche Verhalten, oder andere Spieler oder Teams, in einer verletzenden Art und Weise beleidigen, welche selbst für den in CSGO herrschenden rauen Umgangston unüblich ist, werden bis zu 250 ELO Punkte abgezogen, oder in besonders schwerwiegenden Fällen vom Turnier ausgeschlossen.",
            ]
         },
        {"id": 6, "rule": "Turnierausschluss", "subrules":
            [
                "Alle Programme oder andere nicht technischen Hilfsmittel, welche einem Spieler, oder einem Team als ganzes, einen Vorteil gegenüber anderen Teams verschaffen, sind verboten. Ausgenommen sind Programme welche im allgemeinen Verständnis der CSGO Spieler nicht als Cheats angesehen werden, wie unter anderem Programme zur Kommunikation mit den anderen Spielern außerhalb des ingame-chats, wie Discord oder Teamspeak.",
                "Modifikationen, die innerhalb des CSGO Clients stattfinden, wie unter anderem Jump-Throw-Binds, sind erlaubt.",
                "Das Angreifen des Servers oder der Clients anderer Spieler ist verboten, dazu zählen insbesondere, DDOS Attacken oder ähnliches.",
                "Wenn ein Spieler des Teams gegen die Regeln des §5 verstößt, wird das gesamte Team disqualifiziert und der Spieler wird für alle zukünftigen Turniere gesperrt.",
                "Sollte ein Spieler wegen eines Verstoßes gegen die Regeln des §5 disqualifiziert werden, behalten wir es uns als Veranstalter vor, den betreffenden Spieler nach § 146 StGB wegen Betrugs anzuzeigen.",
            ]
         },
    ]
    return rules
