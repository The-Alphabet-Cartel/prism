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
Temporary utility handler for prism-bot. Provides a !roles command that
lists all roles and their IDs in the guild. Remove after role IDs captured.
----------------------------------------------------------------------------
FILE VERSION: v1.6.0
LAST MODIFIED: 2026-02-23
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import fluxer

from src.managers.config_manager import ConfigManager
from src.managers.logging_config_manager import LoggingConfigManager


def setup(
    bot: fluxer.Bot,
    config_manager: ConfigManager,
    logging_manager: LoggingConfigManager,
) -> None:
    """Register the !roles command listener directly on the bot."""

    log = logging_manager.get_logger("utility_temp")

    @bot.event
    async def on_message(message: fluxer.Message) -> None:
        try:
            if message.author.bot:
                return

            if message.content.strip().lower() != "!roles":
                return

            guild = message.guild
            if guild is None:
                await message.reply("❌ This command must be used in a guild.")
                return

            log.info(f"!roles used by {message.author} in #{message.channel}")

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
        except Exception as e:
            import traceback
            log.error(f"Exception in utility_temp on_message: {e}")
            log.error(traceback.format_exc())
