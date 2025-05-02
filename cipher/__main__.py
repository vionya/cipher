# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import asyncio
import logging

import asyncpraw

from cipher import CipherClient
from cipher.config import reddit, discord, constants
from cipher.utils.formatter import CustomLoggingFormatter

formatter = CustomLoggingFormatter(
    fmt="[{asctime}] [{levelname} {name} {funcName}] {message}"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

for logger_name, level in (
    ("asyncprawcore", logging.INFO),
    ("cipher", logging.INFO),
    ("discord", logging.INFO),
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)


async def main():
    r = asyncpraw.Reddit(**reddit)

    client = CipherClient(r, **constants["kwargs"])
    await client.start(discord["token"])


if __name__ == "__main__":
    asyncio.run(main())
