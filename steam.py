import os
from typing import List, Optional

import requests

STEAM_API_KEY = os.getenv("STEAM_KEY")


class SteamUser:
    def __init__(self, steam_id, name, avatar_url, profile_url):
        self.steam_id = steam_id
        self.name = name
        self.avatar_url = avatar_url
        self.profile_url = profile_url


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
    try:
        if profile_url.endswith("/"):
            profile_url = profile_url[:-1]

        components = profile_url.split("/")

        url_type = components[-2]
        profile_id = components[-1]

        if url_type == "id":
            request = requests.get(
                f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM_API_KEY}&vanityurl={profile_id}"
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
        print(f"Error when getting steam id for profile url: \"{profile_url}\":\n{e}")
        return None


def get_profiles(steam_ids: List[str]) -> list[SteamUser]:
    i = 0
    while i < len(steam_ids):
        steam_id = steam_ids[i]
        if steam_id.startswith("STEAM_0"):
            steam_ids[i] = community_id_to_steam_id(steam_id)
        i += 1

    request = requests.get(
        f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?"
        f"key={STEAM_API_KEY}&" 
        f"steamids={';'.join(steam_ids)}"
    )

    response = request.json()

    profiles = []
    for player in response["response"]["players"]:
        steam_id = player["steamid"]
        name = player["personaname"]
        avatar_url = player["avatarfull"]
        profile_url = player["profileurl"]

        profiles.append(SteamUser(steam_id, name, avatar_url, profile_url))

    return profiles
