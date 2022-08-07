"""
basetui

Bare-bones ncurses tui wrapper.
"""


__version__ = "0.0.1"
__author__ = "Chris Zuelsdorf"


from .logmod import logbuf
from .basetui import basetui
from .tuimanager import supd, get_row_col
