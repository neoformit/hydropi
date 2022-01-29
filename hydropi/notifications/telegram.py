"""Telegram notifications API."""

import requests

from hydropi.config import config


URL = f'https://api.telegram.org/bot{config.TELEGRAM_API_TOKEN}/sendMessage'


def notify(message):
    """Send a message over the Telegram API."""
    requests.post(
        URL,
        data={
            'chat_id': config.TELEGRAM_CHAT_ID,
            'text': message,
        },
    )
