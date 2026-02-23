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
Temporary utility cog for prism-bot. Provides a !roles command that lists
all roles and their IDs in the guild. Remove this cog once role IDs have
been captured and added to configuration.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
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


class UtilityTempCog(commands.Cog):
    """Temporary utility commands for setup and diagnostics. Remove after use."""

    def __init__(
        self,
        bot: commands.Bot,
        config_manager: ConfigManager,
        logging_manager: LoggingConfigManager,
    ) -> None:
        self.bot = bot
        self.config = config_manager
        self.log = logging_manager.get_logger("utility_temp")

    @commands.command(name="roles")
    @commands.has_permissions(administrator=True)
    async def list_roles(self, ctx: commands.Context) -> None:
        """Lists all roles in the guild with their IDs. Admin only."""
        guild = ctx.guild
        if guild is None:
            await ctx.send("❌ This command must be used in a guild.")
            return

        lines = ["**Guild Roles and IDs:**\n```"]
        for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
            lines.append(f"{role.name:<40} {role.id}")
        lines.append("```")

        output = "\n".join(lines)

        # Split if over Discord's 2000 char message limit
        if len(output) > 2000:
            chunks = []
            chunk = ["**Guild Roles and IDs:**\n```"]
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
                line = f"{role.name:<40} {role.id}"
                if sum(len(l) for l in chunk) + len(line) > 1900:
                    chunk.append("```")
                    chunks.append("\n".join(chunk))
                    chunk = ["```"]
                chunk.append(line)
            chunk.append("```")
            chunks.append("\n".join(chunk))
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(output)

        self.log.info(f"!roles command used by {ctx.author} in #{ctx.channel}")

    @list_roles.error
    async def list_roles_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permissions to use this command.")
        else:
            self.log.error(f"Unexpected error in !roles: {error}")


async def setup(
    bot: commands.Bot,
    config_manager: ConfigManager,
    logging_manager: LoggingConfigManager,
) -> None:
    await bot.add_cog(UtilityTempCog(bot, config_manager, logging_manager))
