"""Telegram notifications API."""

import logging
import requests

from hydropi.config import config

logger = logging.getLogger('hydropi')

URL = f'https://api.telegram.org/bot{config.TELEGRAM_API_TOKEN}/sendMessage'


def notify(message):
    """Send a message over the Telegram API."""
    if config.DEVMODE:
        return print(f"DEVMODE: spoof telegram message\n{message}")
    if not config.TELEGRAM_CHAT_ID:
        return logger.info(
            "Telegram notification skipped: no credentials set"
            " in config.yml")
    requests.post(
        URL,
        data={
            'chat_id': config.TELEGRAM_CHAT_ID,
            'text': message,
        },
    )
