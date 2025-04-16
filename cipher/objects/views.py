# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import logging

import discord

from cipher.utils.cache import TimedCache
from cipher.config import constants


log = logging.getLogger("client")


class StartVerification(discord.ui.Modal, title="Begin Verifying"):
    reddit_name = discord.ui.TextInput(
        label="Your Reddit Username", placeholder="u/something", required=True
    )

    def __init__(self, cache: TimedCache):
        self.cache = cache
        super().__init__(custom_id="verify_view:modal")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        name = self.reddit_name.value.removeprefix("u/").strip().casefold()
        self.cache[name] = interaction.user.id
        log.info(f"began verifying @{interaction.user} <-> u/{name}")
        embed = discord.Embed(
            title="Verification Initialized",
            description=constants["strings"]["DISCORD_REDDIT_GUIDE"],
            color=discord.Color.blurple(),
        ).set_footer(
            text="Verification requests will time out after 10 minutes of inactivity"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            view=discord.ui.View().add_item(
                discord.ui.Button(
                    label="DM Verifier Bot on Reddit",
                    emoji="\U0001f4e8",
                    url="http://www.reddit.com/message/compose?to=MegathreadVerifier&subject=Verification%20Request",
                )
            ),
        )


class VerifyView(discord.ui.View):
    cache: TimedCache

    def __init__(self, cache: TimedCache):
        self.cache = cache

        super().__init__(timeout=None)

    @discord.ui.button(
        label="Begin Verifying!",
        emoji="\U0001f517",
        style=discord.ButtonStyle.green,
        custom_id="verify_view:verify",
    )
    async def verify(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(StartVerification(self.cache))
