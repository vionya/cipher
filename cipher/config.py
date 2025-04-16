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


class ConstantsConfig(TypedDict):
    kwargs: KwargsConfig
    strings: dict[str, str]


class KwargsConfig(TypedDict):
    target_channel_id: int
    target_message_id: int


_data = json.load(open("config.json"))

reddit = RedditConfig(_data["reddit"])
discord = DiscordConfig(_data["discord"])
constants = ConstantsConfig(_data["constants"])
