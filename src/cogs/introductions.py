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
Introductions handler for prism-bot. Pure logic class — no event
registration. Called by the dispatcher in main.py.
----------------------------------------------------------------------------
FILE VERSION: v1.8.0
LAST MODIFIED: 2026-02-23
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import fluxer

from src.managers.config_manager import ConfigManager
from src.managers.logging_config_manager import LoggingConfigManager


class IntroductionsHandler:
    """Assigns Saldato role to members posting in #introductions."""

    def __init__(
        self,
        bot: fluxer.Bot,
        config_manager: ConfigManager,
        logging_manager: LoggingConfigManager,
    ) -> None:
        self.bot = bot
        self.log = logging_manager.get_logger("introductions")
        self.guild_id = config_manager.get_int("bot", "guild_id", 0)
        self.introductions_channel_id = config_manager.get_int(
            "channels", "introductions", 0
        )
        self.saldato_role_id = config_manager.get_int("roles", "saldato", 0)

        if not self.guild_id:
            self.log.warning("Guild ID is not configured")
        if not self.introductions_channel_id:
            self.log.warning("Introductions channel ID is not configured")
        if not self.saldato_role_id:
            self.log.warning("Saldato role ID is not configured")

    async def handle(self, message: fluxer.Message) -> None:
        """Process a message. Called by the main dispatcher."""
        # Only act in #introductions
        if message.channel.id != self.introductions_channel_id:
            return

        # Get guild from bot cache
        guild = self.bot.get_guild(self.guild_id)
        if guild is None:
            self.log.error(f"Guild {self.guild_id} not found in cache")
            return

        # Get full member object (has .roles, unlike User)
        member = guild.get_member(message.author.id)
        if member is None:
            self.log.warning(
                f"Could not resolve member for user {message.author.id}"
            )
            return

        # Skip if member already has roles beyond @everyone
        assignable_roles = [r for r in member.roles if r.name != "@everyone"]
        if assignable_roles:
            self.log.debug(
                f"Skipping {member} — already has roles: "
                f"{[r.name for r in assignable_roles]}"
            )
            return

        # Resolve the Saldato role object
        saldato_role = guild.get_role(self.saldato_role_id)
        if saldato_role is None:
            self.log.warning(
                f"Saldato role ID {self.saldato_role_id} not found in guild — "
                "check PRISM_SALDATO_ROLE_ID in .env"
            )
            return

        # Assign role
        try:
            await member.add_roles(
                saldato_role,
                reason="Introduction posted in #introductions",
            )
            self.log.success(  # type: ignore[attr-defined]
                f"Assigned Saldato to {member} (ID: {member.id})"
            )
        except fluxer.Forbidden:
            self.log.error(
                f"Missing permissions to assign Saldato to {member} — "
                "check role hierarchy"
            )
        except fluxer.HTTPException as e:
            self.log.error(f"API error assigning Saldato to {member}: {e}")
