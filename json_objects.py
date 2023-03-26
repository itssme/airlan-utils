from typing import Union

from pydantic import BaseModel


class ServerID(BaseModel):
    id: int


class RconCommand(BaseModel):
    rcon: str
    server_ip: Union[str, None] = "host.docker.internal"
    server_port: int


class SlayPlayer(BaseModel):
    player_name: str
    server_ip: Union[str, None] = "host.docker.internal"
    server_port: int


class MatchInfo(BaseModel):
    team1: int
    team2: int
    best_of: Union[int, None] = None
    check_auths: Union[bool, None] = None
    host: Union[str, None] = None
    from_backup_url: Union[str, None] = None


class TeamInfo(BaseModel):
    name: str
    tag: str


class PlayerInfo(BaseModel):
    steam_id: str
    name: str


class TeamAssignmentInfo(BaseModel):
    team_id: int
    player_id: int


class CompetingInfo(BaseModel):
    team_id: int
    competing: int
