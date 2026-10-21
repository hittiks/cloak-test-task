import logging
import sys
from collections.abc import Callable
from copy import copy
from typing import Literal

import click


class ColorizedFormatter(logging.Formatter):
    """Formatter that adds color coding to log levels for console output."""

    level_name_colors: dict[int, Callable[[str], str]] = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        return True

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(recordcopy)


class ComponentFormatter(ColorizedFormatter):
    """Formatter that adds component name with optional coloring."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
        component_name: str | None = None,
        component_color: str | None = None,
    ):
        self.component_name = component_name or ""
        self.component_color = component_color
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, use_colors=use_colors)

    def _color_component(self, text: str) -> str:
        if not self.use_colors or not self.component_color:
            return text

        cc = self.component_color

        if isinstance(cc, str) and cc.startswith("(") and cc.endswith(")"):
            try:
                r, g, b = [int(x.strip()) for x in cc[1:-1].split(",")]
                # ANSI truecolor: 38;2;R;G;B
                return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
            except Exception: # noqa: BLE001, S110
                pass

        try:
            return click.style(text, fg=cc)
        except TypeError:
            return text

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)

        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))

        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()

        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator

        component = self.component_name or recordcopy.name
        component = self._color_component(component)
        recordcopy.__dict__["component"] = component

        return logging.Formatter.formatMessage(self, recordcopy)
