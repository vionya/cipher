import logging
from typing import cast
import asyncpraw as apraw
import discord
from discord.ext import commands

import cipher
from cipher.objects.views import VerifyView
from cipher.utils.cache import TimedCache
from cipher.utils.timer import periodic
from cipher.config import constants, settings

log = logging.getLogger(__name__)


class Verification(commands.Cog):
    verification_cache: TimedCache[str, int]

    def __init__(self, bot: cipher.CipherClient):
        self.bot = bot

        self.verification_cache = TimedCache[str, int](600)
        if settings["do_verification"]:
            self.bot.add_view(
                VerifyView(self.verification_cache),
                message_id=constants["target_message_id"],
            )

    async def cog_load(self):
        if settings["do_verification"]:
            self.check_verifications.start()

    @periodic(30)
    async def check_verifications(self):
        await self.bot.wait_until_ready()
        if not settings["do_verification"]:
            return

        channel = self.bot.get_channel(constants["target_channel_id"])
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
                user := await self.bot.fetch_user(
                    self.verification_cache[rname]
                )
            ).name.casefold() in content.casefold():
                del self.verification_cache[rname]
                log.info(f"finished verifying @{user} <-> u/{author}")
                embed = discord.Embed(
                    title="User ready to be vetted",
                    description=(
                        f"[u/{author}](https://reddit.com/u/{author})"
                        f" \U0001f517 {user.mention}"
                    ),
                    color=discord.Color.blurple(),
                )
                await channel.send(embed=embed)
        log.debug("finished checking verifications")

    async def fetch_inbox(
        self,
    ) -> list[tuple[apraw.reddit.models.Redditor, str]]:
        output = []
        log.debug("beginning to fetch reddit inbox")
        async for message in self.bot.reddit.inbox.unread():
            if not isinstance(message, apraw.reddit.models.Message):
                continue
            if message.subject.lower() == "verification request":
                if message.author.name.casefold() in self.verification_cache:
                    output.append(
                        (
                            cast(apraw.reddit.models.Redditor, message.author),
                            cast(str, message.body),
                        )
                    )
                    await message.reply(constants["strings"]["REDDIT_PENDING"])
                else:
                    await message.reply(
                        constants["strings"]["REDDIT_NO_REQUEST"]
                    )
            else:
                await message.reply(constants["strings"]["REDDIT_BAD_SUBJECT"])
            await message.mark_read()
        log.debug("finished fetching reddit inbox")
        return output

    @commands.is_owner()
    @commands.command(name="initverify")
    async def init_verify(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        await channel.send(
            constants["strings"]["DISCORD_ENTRYPOINT"],
            view=VerifyView(self.verification_cache),
        )

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     assert self.bot.user
    #     if (
    #         self.bot.owner_id
    #         and message.author.id == self.bot.owner_id
    #         and self.bot.user.mentioned_in(message)
    #     ):
    #         await message.channel.send(
    #             constants["strings"]["DISCORD_ENTRYPOINT"],
    #             view=VerifyView(self.verification_cache),
    #         )


async def setup(bot: cipher.CipherClient):
    await bot.add_cog(Verification(bot))
