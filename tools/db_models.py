from peewee import *

database = SqliteDatabase('events.db')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class PlayerDeath(BaseModel):
    assistedflash = IntegerField(null=True)
    assister = IntegerField(null=True)
    attacker_name = TextField(null=True)
    attacker_steamid = IntegerField(null=True)
    attackerblind = IntegerField(null=True)
    distance = FloatField(null=True)
    dominated = IntegerField(null=True)
    event_name = TextField(null=True)
    file = TextField(null=True)
    headshot = IntegerField(null=True)
    index = IntegerField(index=True, null=True)
    noreplay = IntegerField(null=True)
    noscope = IntegerField(null=True)
    penetrated = IntegerField(null=True)
    player_name = TextField(null=True)
    player_steamid = IntegerField(null=True)
    revenge = IntegerField(null=True)
    round = IntegerField(null=True)
    thrusmoke = IntegerField(null=True)
    tick = IntegerField(null=True)
    weapon = TextField(null=True)
    weapon_fauxitemid = TextField(null=True)
    weapon_itemid = TextField(null=True)
    weapon_originalowner_xuid = TextField(null=True)
    wipe = IntegerField(null=True)

    class Meta:
        table_name = 'player_death'
        primary_key = False

