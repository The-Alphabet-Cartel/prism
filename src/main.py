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
Main entry point for prism-bot. Initialises managers, configures the Fluxer
client, loads cogs, and starts the bot.
----------------------------------------------------------------------------
FILE VERSION: v1.4.0
LAST MODIFIED: 2026-02-22
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import sys

import fluxer

from src.managers.config_manager import create_config_manager
from src.managers.logging_config_manager import create_logging_config_manager


def main() -> None:

    # -------------------------------------------------------------------------
    # Initialise logging (must be first)
    # -------------------------------------------------------------------------
    logging_manager = create_logging_config_manager(app_name="prism-bot")
    log = logging_manager.get_logger("main")

    log.info("prism-bot starting up")

    # -------------------------------------------------------------------------
    # Initialise config
    # -------------------------------------------------------------------------
    try:
        config_manager = create_config_manager()
    except Exception as e:
        log.critical(f"Failed to initialise ConfigManager: {e}")
        sys.exit(1)

    # Reconfigure logging with values from config/env
    logging_manager = create_logging_config_manager(
        log_level=config_manager.get("logging", "level", "INFO"),
        log_format=config_manager.get("logging", "format", "human"),
        log_file=config_manager.get("logging", "file"),
        console_enabled=config_manager.get_bool("logging", "console", True),
        app_name="prism-bot",
    )
    log = logging_manager.get_logger("main")

    # -------------------------------------------------------------------------
    # Validate token
    # -------------------------------------------------------------------------
    token = config_manager.get_token()
    if not token:
        log.critical("Bot token is missing — cannot start")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Initialise Fluxer client
    # -------------------------------------------------------------------------
    intents = fluxer.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = fluxer.Bot(command_prefix=config_manager.get("bot", "command_prefix", "!"), intents=intents)

    # -------------------------------------------------------------------------
    # Load cogs and register events
    # -------------------------------------------------------------------------
    _register_cogs(bot, config_manager, logging_manager, log)

    @bot.event
    async def on_ready() -> None:
        log.success(f"prism-bot connected as {bot.user} (ID: {bot.user.id})")  # type: ignore[attr-defined]

    # -------------------------------------------------------------------------
    # Start — bot.run() is blocking
    # -------------------------------------------------------------------------
    bot.run(token)


def _register_cogs(bot: fluxer.Bot, config_manager, logging_manager, log) -> None:
    from src.cogs.introductions import setup as setup_introductions
    from src.cogs.utility_temp import setup as setup_utility_temp

    try:
        setup_introductions(bot, config_manager, logging_manager)
        log.success("Loaded cog: introductions")  # type: ignore[attr-defined]
    except Exception as e:
        log.error(f"Failed to load introductions cog: {e}")

    try:
        setup_utility_temp(bot, config_manager, logging_manager)
        log.success("Loaded cog: utility_temp (TEMPORARY — remove after setup)")  # type: ignore[attr-defined]
    except Exception as e:
        log.error(f"Failed to load utility_temp cog: {e}")


if __name__ == "__main__":
    main()
