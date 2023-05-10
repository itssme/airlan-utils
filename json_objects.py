from typing import Union, Optional

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
    best_of: Optional[int] = None
    check_auths: Optional[bool] = None
    host: Optional[str] = None
    from_backup_url: Optional[str] = None


class HostInfo(BaseModel):
    ip: str


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
