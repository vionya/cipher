# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import asyncio
import logging

import asyncpraw

from client import MegathreadVerifierClient
from config import reddit, discord, verifier
from formatter import CustomLoggingFormatter

formatter = CustomLoggingFormatter(
    fmt="[{asctime}] [{levelname} {name} {funcName}] {message}"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

for logger_name, level in (
    ("asyncprawcore", logging.DEBUG),
    ("client", logging.DEBUG),
    ("discord", logging.INFO),
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)


async def main():
    r = asyncpraw.Reddit(**reddit)

    client = MegathreadVerifierClient(r, **verifier["kwargs"])
    await client.start(discord["token"])


if __name__ == "__main__":
    asyncio.run(main())
