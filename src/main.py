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
client, loads handlers, and starts the bot.

Single on_message dispatcher pattern used because fluxer-py only supports
one registered handler per event type.
----------------------------------------------------------------------------
FILE VERSION: v1.7.0
LAST MODIFIED: 2026-02-23
BOT: prism-bot
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/bragi
============================================================================
"""

import sys
import traceback

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

    bot = fluxer.Bot(
        command_prefix=config_manager.get("bot", "command_prefix", "!"),
        intents=intents,
    )

    # -------------------------------------------------------------------------
    # Initialise handlers (pure logic, no event registration)
    # -------------------------------------------------------------------------
    from src.cogs.introductions import IntroductionsHandler
    from src.cogs.utility_temp import UtilityTempHandler

    introductions = IntroductionsHandler(config_manager, logging_manager)
    log.success("Loaded handler: introductions")  # type: ignore[attr-defined]

    utility_temp = UtilityTempHandler(logging_manager)
    log.success("Loaded handler: utility_temp (TEMPORARY — remove after setup)")  # type: ignore[attr-defined]

    # -------------------------------------------------------------------------
    # Single on_message dispatcher — routes to all handlers in order
    # -------------------------------------------------------------------------
    @bot.event
    async def on_message(message: fluxer.Message) -> None:
        if message.author.bot:
            return
        try:
            await introductions.handle(message)
        except Exception as e:
            log.error(f"introductions handler error: {e}\n{traceback.format_exc()}")
        try:
            await utility_temp.handle(message)
        except Exception as e:
            log.error(f"utility_temp handler error: {e}\n{traceback.format_exc()}")

    # -------------------------------------------------------------------------
    # on_error — surface any remaining unhandled exceptions
    # -------------------------------------------------------------------------
    @bot.event
    async def on_error(event: str, *args, **kwargs) -> None:
        log.error(f"Unhandled exception in event '{event}':\n{traceback.format_exc()}")

    # -------------------------------------------------------------------------
    # on_ready
    # -------------------------------------------------------------------------
    @bot.event
    async def on_ready() -> None:
        log.success(f"prism-bot connected as {bot.user} (ID: {bot.user.id})")  # type: ignore[attr-defined]

    # -------------------------------------------------------------------------
    # Start — bot.run() is blocking
    # -------------------------------------------------------------------------
    bot.run(token)


if __name__ == "__main__":
    main()
