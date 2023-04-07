import os
from peewee import *



database = PostgresqlDatabase(os.getenv('POSTGRES_DB', 'postgres'), **{'host': os.getenv('POSTGRES_DB_HOST', 'db'), 'port': int(os.getenv('POSTGRES_DB_PORT', '5432')), 'user': os.getenv('POSTGRES_USER', 'postgres'), 'password': os.getenv('POSTGRES_PASSWORD', 'pass')})


class UnknownField(object):

    def __init__(self, *_, **__): pass



class BaseModel(Model):

    class Meta:

        database = database



class Account(BaseModel):

    password = TextField()

    role = TextField(constraints=[SQL("DEFAULT 'user'::text")])

    username = TextField(primary_key=True)

    verification_code = TextField()

    verified = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)



    class Meta:

        table_name = 'account'



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



    class Meta:

        table_name = 'host'



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



class Match(BaseModel):

    best_out_of = IntegerField()

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



class Server(BaseModel):

    container_name = TextField(null=True)

    gslt_token = TextField(null=True)

    ip = ForeignKeyField(column_name='ip', constraints=[SQL("DEFAULT 'host.docker.internal'::text")], field='ip', model=Host, null=True)

    match = ForeignKeyField(column_name='match', field='id', model=Match, null=True)

    port = IntegerField(constraints=[SQL("DEFAULT '-1'::integer")], null=True)



    class Meta:

        table_name = 'server'



class Stats(BaseModel):

    match = ForeignKeyField(column_name='match', field='id', model=Match, null=True)

    player = ForeignKeyField(column_name='player', field='id', model=Player, null=True)

    type = IntegerField()



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


