import discord
from discord import app_commands
from discord.ext import commands

from cipher.config import constants


class Messenger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(
        user="The user to send the message to",
        content="The content of the message to send",
    )
    @app_commands.command(
        name="modmessage",
        description="Send a single message to a user through the bot",
    )
    async def messenger_outreach(
        self, interaction: discord.Interaction, user: discord.User, content: str
    ):
        assert interaction.guild
        try:
            embed = (
                discord.Embed(
                    description=content,
                    color=discord.Color.blurple(),
                )
                .add_field(
                    name="Details",
                    value=constants["strings"][
                        "DISCORD_MESSENGER_DISCLAIMER"
                    ].format(server_name=str(interaction.guild)),
                    inline=False,
                )
                .set_author(
                    name=f"Directed Modmail from {interaction.guild}",
                    icon_url=(
                        interaction.guild.icon.url
                        if interaction.guild.icon
                        else None
                    ),
                )
            )
            await user.send(embed=embed)
            await interaction.response.send_message(
                f"Message sent to {user.mention}.", ephemeral=False
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"Could not send message to {user.mention}. They may have DMs disabled, or the bot blocked",
                ephemeral=False,
            )
        except Exception as e:
            # oops
            raise e


async def setup(bot: commands.Bot):
    await bot.add_cog(Messenger(bot))
