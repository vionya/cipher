# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import logging

import discord
import asyncpraw
from discord.ext import commands

from cipher.config import settings

log = logging.getLogger(__name__)


class CipherClient(commands.Bot):
    reddit: asyncpraw.Reddit
    owner_id: int | None

    def __init__(
        self,
        reddit: asyncpraw.Reddit,
        **kwargs,
    ):
        kwargs["intents"] = discord.Intents.default()
        kwargs["help_command"] = None
        kwargs["command_prefix"] = commands.when_mentioned
        kwargs["allowed_mentions"] = discord.AllowedMentions.none()

        super().__init__(**kwargs)

        self.reddit = reddit
        self.owner_id = None

    async def setup_hook(self):
        for extension in settings["load_order"]:
            await self.load_extension(extension)

    async def on_ready(self):
        self.owner_id = (await self.application_info()).owner.id
        await self.tree.sync()
