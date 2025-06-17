# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
from __future__ import annotations

import json
from typing import TypedDict


class RedditConfig(TypedDict):
    client_id: str
    client_secret: str
    password: str
    user_agent: str
    username: str


class DiscordConfig(TypedDict):
    token: str


class SettingsConfig(TypedDict):
    do_verification: bool
    load_order: list[str]
    prefix: str


class ConstantsConfig(TypedDict):
    strings: dict[str, str]
    target_channel_id: int
    target_message_id: int


_data = json.load(open("config.json"))

reddit = RedditConfig(_data["reddit"])
discord = DiscordConfig(_data["discord"])
settings = SettingsConfig(_data["settings"])
constants = ConstantsConfig(_data["constants"])
