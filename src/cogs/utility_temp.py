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
Temporary utility handler for prism-bot. Pure logic class — no event
registration. Called by the dispatcher in main.py. Remove after setup.
----------------------------------------------------------------------------
FILE VERSION: v1.9.0
LAST MODIFIED: 2026-02-23
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import fluxer

from src.managers.config_manager import ConfigManager
from src.managers.logging_config_manager import LoggingConfigManager


class UtilityTempHandler:
    """Lists guild roles via !roles command. Temporary — remove after setup."""

    def __init__(
        self,
        bot: fluxer.Bot,
        config_manager: ConfigManager,
        logging_manager: LoggingConfigManager,
    ) -> None:
        self.bot = bot
        self.log = logging_manager.get_logger("utility_temp")
        self.guild_id = config_manager.get_int("bot", "guild_id", 0)

        if not self.guild_id:
            self.log.warning("Guild ID is not configured — !roles will not work")

    async def handle(self, message: fluxer.Message) -> None:
        """Process a message. Called by the main dispatcher."""
        if message.content.strip().lower() != "!roles":
            return

        self.log.info(f"!roles used by {message.author} in #{message.channel}")

        guild_id = message.channel.guild_id
        try:
            guild = await self.bot.fetch_guild(guild_id)
        except Exception as e:
            await message.reply(f"❌ Could not fetch guild: {e}")
            return

        lines = ["**Guild Roles and IDs:**\n```"]
        for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
            lines.append(f"{role.name:<40} {role.id}")
        lines.append("```")

        output = "\n".join(lines)

        if len(output) <= 2000:
            await message.reply(output)
        else:
            chunks = []
            chunk = ["**Guild Roles and IDs:**\n```"]
            for role in sorted(
                guild.roles, key=lambda r: r.position, reverse=True
            ):
                line = f"{role.name:<40} {role.id}"
                if sum(len(ln) for ln in chunk) + len(line) > 1900:
                    chunk.append("```")
                    chunks.append("\n".join(chunk))
                    chunk = ["```"]
                chunk.append(line)
            chunk.append("```")
            chunks.append("\n".join(chunk))
            for chunk in chunks:
                await message.reply(chunk)
