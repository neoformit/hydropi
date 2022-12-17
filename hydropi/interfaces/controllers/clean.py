"""Clean up old controller files.

Should run at startup.
"""

import os
import logging
from hydropi.config import config

DEED_ROOT = os.path.join(config.TEMP_DIR, 'deeds')

logger = logging.getLogger('hydropi')


def deeds():
    """Remove stale deed files.

    These could be remnants of an interrupted process.
    """
    for root, dirs, files in os.walk(DEED_ROOT):
        for f in files:
            path = os.path.join(root, f)
            try:
                os.remove(path)
                logger.info(f"Removed stale deed: {path}")
            except Exception as exc:
                logger.warning(
                    f"Error removing deed file: {path}")
