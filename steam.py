import logging
import os
from typing import List, Optional

import requests

from utils import db

STEAM_API_KEY = os.getenv("STEAM_KEY", "DEV")

if STEAM_API_KEY == "DEV":
    logging.warning("No steam api key found, disabling steam features")


def steam_id_to_community_id(steam_id: str) -> Optional[str]:
    if steam_id is None:
        return None

    steam_id = int(steam_id)
    community_id = steam_id - 76561197960265728
    community_id_1 = int(community_id % 2)
    community_id_2 = int((community_id - community_id_1) / 2)
    return f"STEAM_0:{community_id_1}:{community_id_2}"


def community_id_to_steam_id(community_id: str) -> Optional[str]:
    if community_id is None:
        return None

    steam_id_1, steam_id_2 = community_id.split(":")[1:]
    steam_id_64 = int(steam_id_1) + 2 * int(steam_id_2) + 76561197960265728

    return str(steam_id_64)


def get_steam_id(profile_url: str) -> Optional[str]:
    if STEAM_API_KEY == "DEV":
        return None

    try:
        if profile_url.endswith("/"):
            profile_url = profile_url[:-1]

        components = profile_url.split("/")

        url_type = components[-2]
        profile_id = components[-1]

        if url_type == "id":
            params = {"key": STEAM_API_KEY, "vanityurl": profile_id}
            request = requests.get(
                f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/", params=params
            )
            response = request.json()
            if response["response"]["success"] == 1:
                return steam_id_to_community_id(response["response"]["steamid"])
            else:
                return None
        elif url_type == "profiles":
            return steam_id_to_community_id(profile_id)
        else:
            return None
    except Exception as e:
        logging.error(f"Error when getting steam id for profile url: \"{profile_url}\":\n{e}")
        return None


def get_team_steam_profiles(team_id: int) -> List[db.Player]:
    players = db.get_team_players(team_id)
    player_steam_ids = [player.steam_id for player in players]
    steam_profiles = get_profiles(player_steam_ids)

    steam_profiles.sort(key=lambda x: x.steam_id)

    return steam_profiles


def get_profiles(steam_ids: List[str]) -> List[db.Player]:
    if STEAM_API_KEY == "DEV":
        return []

    for i in range(0, len(steam_ids)):
        steam_id = steam_ids[i]
        if steam_id.startswith("STEAM_0"):
            steam_ids[i] = community_id_to_steam_id(steam_id)

    params = {"key": STEAM_API_KEY, "steamids": ";".join(steam_ids)}
    request = requests.get(
        f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002", params=params
    )

    if request.status_code != 200:
        logging.error(f"Error when getting steam profiles: {request.status_code}, {request.text}")
        return []

    response = request.json()

    profiles: List[db.Player] = []
    for player in response["response"]["players"]:
        steam_id = player["steamid"]
        name = player["personaname"]
        avatar_url = player["avatarfull"]
        profile_url = player["profileurl"]

        profiles.append(db.Player(steam_id=steam_id, steam_name=name, avatar_url=avatar_url, profile_url=profile_url))

    return profiles
