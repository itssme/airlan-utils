import os
import requests

STEAM_API_KEY = os.getenv("STEAM_KEY")


class SteamUser:
    def __init__(self, steam_id, name, avatar_url, profile_url):
        self.steam_id = steam_id
        self.name = name
        self.avatar_url = avatar_url
        self.profile_url = profile_url


def get_steam_id(profile_url):
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
            return response["response"]["steamid"]
        else:
            return None
    elif url_type == "profiles":
        return profile_id
    else:
        return None


def get_profiles(steam_ids):
    request = requests.get(
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={[steam_id for steam_id in steam_ids]}"
    )
    response = request.json()

    profiles = []
    for player in response["response"]["players"]:
        steam_id = player["steamid"]
        name = player["personaname"]
        avatar_url = player["avatarfull"]
        profile_url = player["profileurl"]

        profiles.append(SteamUser(steam_id, name, avatar_url, profile_url).__dict__)

    return profiles
