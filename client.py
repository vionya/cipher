# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import logging
from typing import cast

import discord
import asyncpraw

from cache import TimedCache
from timer import periodic
from view import VerifyView
from config import verifier

log = logging.getLogger("client")


class MegathreadVerifierClient(discord.Client):
    verification_cache: TimedCache
    reddit: asyncpraw.Reddit
    target_channel_id: int
    owner_id: int | None

    def __init__(
        self,
        reddit: asyncpraw.Reddit,
        target_channel_id: int,
        target_message_id: int,
        **kwargs,
    ):
        kwargs["intents"] = discord.Intents.default()

        super().__init__(**kwargs)

        self.reddit = reddit
        self.verification_cache = TimedCache(600)
        self.target_channel_id = target_channel_id
        self.owner_id = None
        self.add_view(VerifyView(self.verification_cache), message_id=target_message_id)

    async def setup_hook(self):
        self.check_verifications.start()

    async def on_ready(self):
        self.owner_id = (await self.application_info()).owner.id

    @periodic(30)
    async def check_verifications(self):
        await self.wait_until_ready()

        channel = self.get_channel(self.target_channel_id)
        if channel is None:
            log.error("target channel is None, skipping")
            return
        if not isinstance(channel, discord.abc.Messageable):
            log.error("target channel is not a Messageable object, skipping")
            return

        log.debug("about to fetch inbox")
        messages = await self.fetch_inbox()
        for author, content in messages:
            rname = author.name.casefold()
            if rname not in self.verification_cache:
                continue
            if (
                user := await self.fetch_user(self.verification_cache[rname])
            ).name.casefold() in content.casefold():
                del self.verification_cache[rname]
                log.info(f"finished verifying @{user} <-> u/{author}")
                embed = discord.Embed(
                    title=f"User ready to be vetted",
                    description=f"[u/{author}](https://reddit.com/u/{author}) \U0001f517 {user.mention}",
                    color=discord.Color.blurple(),
                )
                await channel.send(embed=embed)
        log.debug("finished checking verifications")

    async def fetch_inbox(
        self,
    ) -> list[tuple[asyncpraw.reddit.models.Redditor, str]]:
        output = []
        log.debug("beginning to fetch reddit inbox")
        async for message in self.reddit.inbox.unread():
            if not isinstance(message, asyncpraw.reddit.models.Message):
                continue
            if message.subject.lower() == "verification request":
                if message.author.name.casefold() in self.verification_cache:
                    output.append(
                        (
                            cast(asyncpraw.reddit.models.Redditor, message.author),
                            cast(str, message.body),
                        )
                    )
                    await message.reply(verifier["strings"]["REDDIT_PENDING"])
                else:
                    await message.reply(verifier["strings"]["REDDIT_NO_REQUEST"])
            else:
                await message.reply(verifier["strings"]["REDDIT_BAD_SUBJECT"])
            await message.mark_read()
        log.debug("finished fetching reddit inbox")
        return output

    async def on_message(self, message: discord.Message):
        assert self.user
        if (
            self.owner_id
            and message.author.id == self.owner_id
            and self.user.mentioned_in(message)
        ):
            await message.channel.send(
                verifier["strings"]["DISCORD_ENTRYPOINT"],
                view=VerifyView(self.verification_cache),
            )
