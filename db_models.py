
from contextvars import ContextVar
from peewee import *

import os
import peewee

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


database = PostgresqlDatabase(os.getenv('POSTGRES_DB', 'postgres'),
                              **{'host': os.getenv('POSTGRES_DB_HOST', 'db'),
                                 'port': int(os.getenv('POSTGRES_DB_PORT', '5432')),
                                 'user': os.getenv('POSTGRES_USER', 'postgres'),
                                 'password': os.getenv('POSTGRES_PASSWORD', 'pass')})
database._state = PeeweeConnectionState()







class UnknownField(object):

    def __init__(self, *_, **__): pass



class BaseModel(Model):

    class Meta:

        database = database



class YoyoLog(BaseModel):

    comment = CharField(null=True)

    created_at_utc = DateTimeField(null=True)

    hostname = CharField(null=True)

    id = CharField(primary_key=True)

    migration_hash = CharField(null=True)

    migration_id = CharField(null=True)

    operation = CharField(null=True)

    username = CharField(null=True)



    class Meta:

        table_name = '_yoyo_log'



class YoyoMigration(BaseModel):

    applied_at_utc = DateTimeField(null=True)

    migration_hash = CharField(primary_key=True)

    migration_id = CharField(null=True)



    class Meta:

        table_name = '_yoyo_migration'



class YoyoVersion(BaseModel):

    installed_at_utc = DateTimeField(null=True)

    version = AutoField()



    class Meta:

        table_name = '_yoyo_version'



class Account(BaseModel):

    password = TextField()

    password_reset_token = TextField(null=True)

    role = TextField(constraints=[SQL("DEFAULT 'user'::text")])

    username = TextField(primary_key=True)

    verification_code = TextField()

    verified = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)



    class Meta:

        table_name = 'account'



class ArticleType(BaseModel):

    available_quantity = IntegerField()

    description = TextField()

    image = TextField()

    max_order_quantity = IntegerField()

    name = TextField()

    price = DoubleField()



    class Meta:

        table_name = 'article_type'



class Team(BaseModel):

    account = ForeignKeyField(column_name='account', field='username', model=Account)

    competing = IntegerField(constraints=[SQL("DEFAULT 2")], null=True)

    elo = IntegerField(constraints=[SQL("DEFAULT 1000")], null=True)

    locked_changes = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    locked_changes_time = IntegerField(null=True)

    name = TextField(unique=True)

    paid_registration_fee = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    registration_fee_rnd = TextField()

    sponsored = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    tag = TextField()

    verified = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)



    class Meta:

        table_name = 'team'



class ArticleOrder(BaseModel):

    article = ForeignKeyField(column_name='article', constraints=[SQL("DEFAULT nextval('article_order_article_seq'::regclass)")], field='id', model=ArticleType)

    quantity = IntegerField()

    team = ForeignKeyField(column_name='team', constraints=[SQL("DEFAULT nextval('article_order_team_seq'::regclass)")], field='id', model=Team)



    class Meta:

        table_name = 'article_order'

        indexes = (

            (('team', 'article'), True),

        )



class Map(BaseModel):

    description = TextField(constraints=[SQL("DEFAULT ''::text")], null=True)

    image = CharField()

    name = CharField()



    class Meta:

        table_name = 'map'



class Beo1Vote(BaseModel):

    ban_1 = ForeignKeyField(column_name='ban_1', field='id', model=Map, null=True)

    ban_2 = ForeignKeyField(backref='map_ban_2_set', column_name='ban_2', field='id', model=Map, null=True)

    ban_3 = ForeignKeyField(backref='map_ban_3_set', column_name='ban_3', field='id', model=Map, null=True)

    ban_4 = ForeignKeyField(backref='map_ban_4_set', column_name='ban_4', field='id', model=Map, null=True)

    ban_5 = ForeignKeyField(backref='map_ban_5_set', column_name='ban_5', field='id', model=Map, null=True)

    pick_6 = ForeignKeyField(backref='map_pick_6_set', column_name='pick_6', field='id', model=Map, null=True)



    class Meta:

        table_name = 'beo1_vote'



class Beo3Vote(BaseModel):

    ban_1 = ForeignKeyField(column_name='ban_1', field='id', model=Map, null=True)

    ban_2 = ForeignKeyField(backref='map_ban_2_set', column_name='ban_2', field='id', model=Map, null=True)

    ban_5 = ForeignKeyField(backref='map_ban_5_set', column_name='ban_5', field='id', model=Map, null=True)

    ban_6 = ForeignKeyField(backref='map_ban_6_set', column_name='ban_6', field='id', model=Map, null=True)

    pick_3 = ForeignKeyField(backref='map_pick_3_set', column_name='pick_3', field='id', model=Map, null=True)

    pick_4 = ForeignKeyField(backref='map_pick_4_set', column_name='pick_4', field='id', model=Map, null=True)

    pick_7 = ForeignKeyField(backref='map_pick_7_set', column_name='pick_7', field='id', model=Map, null=True)



    class Meta:

        table_name = 'beo3_vote'



class Config(BaseModel):

    key = TextField(primary_key=True)

    value = TextField()



    class Meta:

        table_name = 'config'



class FoodType(BaseModel):

    description = TextField()

    name = TextField()

    price = DoubleField()



    class Meta:

        table_name = 'food_type'



class Player(BaseModel):

    avatar_url = TextField()

    last_updated = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    name = TextField()

    profile_url = TextField()

    steam_id = TextField(unique=True)

    steam_name = TextField()



    class Meta:

        table_name = 'player'



class FoodOrder(BaseModel):

    food = ForeignKeyField(column_name='food', field='id', model=FoodType, null=True)

    player = ForeignKeyField(column_name='player', field='id', model=Player, null=True)



    class Meta:

        table_name = 'food_order'



class Host(BaseModel):

    ip = TextField(primary_key=True)

    port = IntegerField(constraints=[SQL("DEFAULT 5000")])



    class Meta:

        table_name = 'host'



class Match(BaseModel):

    best_out_of = IntegerField()

    current_score_team1 = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    current_score_team2 = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    finished = IntegerField(constraints=[SQL("DEFAULT '-1'::integer")], null=True)

    matchid = TextField(unique=True)

    name = TextField()

    number_in_map_series = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    series_score_team1 = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    series_score_team2 = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    team1 = ForeignKeyField(column_name='team1', field='id', model=Team, null=True)

    team2 = ForeignKeyField(backref='team_team2_set', column_name='team2', field='id', model=Team, null=True)



    class Meta:

        table_name = 'match'



class ScheduledMatch(BaseModel):

    beo1_vote = ForeignKeyField(column_name='beo1_vote', field='id', model=Beo1Vote, null=True)

    beo3_vote = ForeignKeyField(column_name='beo3_vote', field='id', model=Beo3Vote, null=True)

    best_out_of = IntegerField()

    description = TextField(constraints=[SQL("DEFAULT ''::text")], null=True)

    match = ForeignKeyField(column_name='match', field='id', model=Match, null=True)

    match_group = IntegerField(null=True)

    status = CharField(constraints=[SQL("DEFAULT 'scheduled'::character varying")], null=True)

    team1 = ForeignKeyField(column_name='team1', field='id', model=Team)

    team2 = ForeignKeyField(backref='team_team2_set', column_name='team2', field='id', model=Team)



    class Meta:

        table_name = 'scheduled_match'



class Server(BaseModel):

    container_name = TextField(null=True)

    gslt_token = TextField(null=True)

    ip = ForeignKeyField(column_name='ip', constraints=[SQL("DEFAULT 'host.docker.internal'::text")], field='ip', model=Host, null=True)

    match = ForeignKeyField(column_name='match', field='id', model=Match, null=True)

    port = IntegerField(constraints=[SQL("DEFAULT '-1'::integer")], null=True)



    class Meta:

        table_name = 'server'



class Stats(BaseModel):

    _1k = IntegerField(column_name='1k', constraints=[SQL("DEFAULT 0")])

    _1v1 = IntegerField(column_name='1v1', constraints=[SQL("DEFAULT 0")])

    _1v2 = IntegerField(column_name='1v2', constraints=[SQL("DEFAULT 0")])

    _1v3 = IntegerField(column_name='1v3', constraints=[SQL("DEFAULT 0")])

    _1v4 = IntegerField(column_name='1v4', constraints=[SQL("DEFAULT 0")])

    _1v5 = IntegerField(column_name='1v5', constraints=[SQL("DEFAULT 0")])

    _2k = IntegerField(column_name='2k', constraints=[SQL("DEFAULT 0")])

    _3k = IntegerField(column_name='3k', constraints=[SQL("DEFAULT 0")])

    _4k = IntegerField(column_name='4k', constraints=[SQL("DEFAULT 0")])

    _5k = IntegerField(column_name='5k', constraints=[SQL("DEFAULT 0")])

    assists = IntegerField(constraints=[SQL("DEFAULT 0")])

    bomb_defuses = IntegerField(constraints=[SQL("DEFAULT 0")])

    bomb_plants = IntegerField(constraints=[SQL("DEFAULT 0")])

    damage = IntegerField(constraints=[SQL("DEFAULT 0")])

    deaths = IntegerField(constraints=[SQL("DEFAULT 0")])

    enemies_flashed = IntegerField(constraints=[SQL("DEFAULT 0")])

    first_deaths_ct = IntegerField(constraints=[SQL("DEFAULT 0")])

    first_deaths_t = IntegerField(constraints=[SQL("DEFAULT 0")])

    first_kills_ct = IntegerField(constraints=[SQL("DEFAULT 0")])

    first_kills_t = IntegerField(constraints=[SQL("DEFAULT 0")])

    flash_assists = IntegerField(constraints=[SQL("DEFAULT 0")])

    friendlies_flashed = IntegerField(constraints=[SQL("DEFAULT 0")])

    headshot_kills = IntegerField(constraints=[SQL("DEFAULT 0")])

    kast = IntegerField(constraints=[SQL("DEFAULT 0")])

    kills = IntegerField(constraints=[SQL("DEFAULT 0")])

    knife_kills = IntegerField(constraints=[SQL("DEFAULT 0")])

    map_number = IntegerField(constraints=[SQL("DEFAULT 0")])

    match = ForeignKeyField(column_name='match', field='id', model=Match, null=True)

    mvp = IntegerField(constraints=[SQL("DEFAULT 0")])

    player = ForeignKeyField(column_name='player', field='id', model=Player, null=True)

    rounds_played = IntegerField(constraints=[SQL("DEFAULT 0")])

    score = IntegerField(constraints=[SQL("DEFAULT 0")])

    suicides = IntegerField(constraints=[SQL("DEFAULT 0")])

    team_kills = IntegerField(constraints=[SQL("DEFAULT 0")])

    trade_kills = IntegerField(constraints=[SQL("DEFAULT 0")])

    utility_damage = IntegerField(constraints=[SQL("DEFAULT 0")])



    class Meta:

        table_name = 'stats'



class TeamAssignment(BaseModel):

    player = ForeignKeyField(column_name='player', field='id', model=Player)

    team = ForeignKeyField(column_name='team', field='id', model=Team)



    class Meta:

        table_name = 'team_assignment'

        indexes = (

            (('team', 'player'), True),

        )

        primary_key = CompositeKey('player', 'team')



class YoyoLock(BaseModel):

    ctime = DateTimeField(null=True)

    locked = AutoField()

    pid = IntegerField()



    class Meta:

        table_name = 'yoyo_lock'


