"""
============================================================================
Bragi: Bot Infrastructure for The Alphabet Cartel
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.net
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Welcome  → Greet and orient new members to our chosen family
    Moderate → Support staff with tools that keep our space safe
    Support  → Connect members to resources, information, and each other
    Sustain  → Run reliably so our community always has what it needs

============================================================================
Introductions cog for prism-bot. Listens for messages in the #introductions
channel and assigns the Saldato role to members who post there.
----------------------------------------------------------------------------
FILE VERSION: v1.1.0
LAST MODIFIED: 2026-02-22
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import discord
from discord.ext import commands

from src.managers.config_manager import ConfigManager
from src.managers.logging_config_manager import LoggingConfigManager


class IntroductionsCog(commands.Cog):
    """Assigns the Saldato role when a member posts in #introductions."""

    def __init__(
        self,
        bot: commands.Bot,
        config_manager: ConfigManager,
        logging_manager: LoggingConfigManager,
    ) -> None:
        self.bot = bot
        self.config = config_manager
        self.log = logging_manager.get_logger("introductions")

        self.introductions_channel_id = config_manager.get_int("channels", "introductions")
        self.saldato_role_id = config_manager.get_int("roles", "saldato")

        if not self.introductions_channel_id:
            self.log.warning("Introductions channel ID is not configured")
        if not self.saldato_role_id:
            self.log.warning("Saldato role ID is not configured")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore bots
        if message.author.bot:
            return

        # Only act in the introductions channel
        if message.channel.id != self.introductions_channel_id:
            return

        guild = message.guild
        if guild is None:
            return

        member = message.author

        # Resolve the Saldato role
        saldato_role = guild.get_role(self.saldato_role_id)
        if saldato_role is None:
            self.log.error(
                f"Saldato role ID {self.saldato_role_id} not found in guild {guild.id}"
            )
            return

        # Skip if the member already has any roles beyond @everyone
        assignable_roles = [r for r in member.roles if r.name != "@everyone"]
        if assignable_roles:
            self.log.debug(
                f"{member} already has roles {[r.name for r in assignable_roles]} — skipping"
            )
            return

        # Assign the role
        try:
            await member.add_roles(saldato_role, reason="Introduction posted in #introductions")
            self.log.success(  # type: ignore[attr-defined]
                f"Assigned Saldato to {member} (ID: {member.id})"
            )
        except discord.Forbidden:
            self.log.error(f"Missing permissions to assign Saldato role to {member}")
        except discord.HTTPException as e:
            self.log.error(f"Failed to assign Saldato role to {member}: {e}")


async def setup(
    bot: commands.Bot,
    config_manager: ConfigManager,
    logging_manager: LoggingConfigManager,
) -> None:
    await bot.add_cog(IntroductionsCog(bot, config_manager, logging_manager))
