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
Introductions handler for prism-bot. Assigns the Saldato role to members
who post in #introductions and have no existing roles beyond @everyone.
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
    """Register the introductions on_message listener directly on the bot."""

    log = logging_manager.get_logger("introductions")

    # Read channel and role IDs from config
    introductions_channel_id = config_manager.get_int(
        "channels", "introductions", 0
    )
    saldato_role_id = config_manager.get_int("roles", "saldato", 0)

    if not introductions_channel_id:
        log.warning("Introductions channel ID is not configured")
    if not saldato_role_id:
        log.warning("Saldato role ID is not configured")

    @bot.event
    async def on_message(message: fluxer.Message) -> None:
        # Ignore bots
        if message.author.bot:
            return

        # Only act in #introductions
        if message.channel.id != introductions_channel_id:
            return

        # Resolve member
        member = message.author
        if member is None:
            return

        # Skip if member already has roles beyond @everyone
        assignable_roles = [r for r in member.roles if r.name != "@everyone"]
        if assignable_roles:
            log.debug(
                f"Skipping {member} — already has roles: "
                f"{[r.name for r in assignable_roles]}"
            )
            return

        # Resolve the Saldato role object
        guild = message.guild
        if guild is None:
            return

        saldato_role = guild.get_role(saldato_role_id)
        if saldato_role is None:
            log.warning(
                f"Saldato role ID {saldato_role_id} not found in guild — "
                "check PRISM_SALDATO_ROLE_ID in .env"
            )
            return

        # Assign role
        try:
            await member.add_roles(
                saldato_role,
                reason="Introduction posted in #introductions",
            )
            log.success(  # type: ignore[attr-defined]
                f"Assigned Saldato to {member} (ID: {member.id})"
            )
        except fluxer.Forbidden:
            log.error(
                f"Missing permissions to assign Saldato to {member} — "
                "check role hierarchy"
            )
        except fluxer.HTTPException as e:
            log.error(f"API error assigning Saldato to {member}: {e}")
