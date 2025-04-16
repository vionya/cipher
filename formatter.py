# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
from enum import Enum
from logging import Formatter, LogRecord


class Color(Enum):
    Reset = "0"
    Purple = "38;2;162;155;254"
    Green = "38;2;186;230;126"
    Cyan = "38;2;92;207;230"
    Grey = "38;2;112;122;140"
    Silver = "38;2;92;103;115"
    Tan = "38;2;255;230;179"
    Orange = "38;2;255;167;89"
    Red = "38;2;255;51;51"

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = f"\033[{value}m"
        return obj

    def __call__(self, string: str):
        """
        Apply the ANSI color to the provided string

        Trailing resets are provided as well

        ```py
        >>> Color.PURPLE("foo")
        "\\033[38;2;162;155;254mfoo\\033[0m"
        ```
        """
        return f"{self.value}{string}{Color.Reset.value}"


class CustomLoggingFormatter(Formatter):
    COLORS = {
        "DEBUG": Color.Silver,
        "INFO": Color.Green,
        "WARNING": Color.Tan,
        "ERROR": Color.Orange,
        "CRITICAL": Color.Red,
    }

    def __init__(self, **kwargs):
        kwargs["style"] = "{"
        kwargs["datefmt"] = Color.Cyan("%d-%m-%Y %H:%M:%S")
        super().__init__(**kwargs)

    def format(self, record: LogRecord):
        record.asctime = Color.Cyan(self.formatTime(record, self.datefmt))
        record.msg = Color.Grey(record.msg)
        record.name = Color.Purple(record.name)
        record.levelname = self.COLORS[record.levelname](record.levelname)
        return super().format(record)
