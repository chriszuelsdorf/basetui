import configparser
from datetime import datetime
import curses
import os

from .logmod import logbuf
from .tuimanager import curses_main


class basetui:
    def __init__(self, basepath: str, handler: callable) -> None:
        """Init Method.

        Args:
            basepath (str): The path to the base folder; config.ini should be here, and your logs will go here
            handler (callable): Your callable input handler, which should take **{'stdscr': _curses.window, 'colorinfo': dict, 'logMod': logbuf, 'buf': str} as argument(s).

        Raises:
            ValueError: _description_
            FileNotFoundError: _description_
        """

        # Read config file
        config = configparser.ConfigParser()
        config.read(
            basepath + "/config.ini"
        )  # if this fails, you don't have a real config file

        # Assert contents
        if (
            "Startup" not in config
            or "logfile" not in config["Startup"]
            or "loglevel" not in config["Startup"]
        ):
            raise ValueError(
                "Config file is present but missing keys, require Startup/logfile and Startup/loglevel"
            )

        # Get logfile path for this run; replace date if necessary.
        LOGFILE = basepath + config["Startup"]["logfile"].replace(
            "{date}",
            str(datetime.now())
            .replace(" ", "_")
            .replace("-", "")
            .replace(":", "")
            .replace(".", "_"),
        )
        logbase = "/".join(LOGFILE.split("/")[:-1])

        # If the folder tree to this path does not exist, force the user to create it.
        if not os.path.exists(logbase):
            raise FileNotFoundError(
                f"Make sure the specified log path exists: `{logbase}`"
            )

        # setup logger
        logMod = logbuf(LOGFILE, int(config["Startup"]["loglevel"]))

        # extract minimum window dimensions
        WINDOW_MINW = int(config["Window Spec"]["min_width"])
        WINDOW_MINH = int(config["Window Spec"]["min_height"])

        # run wrapper and finally, flush.
        try:
            curses.wrapper(
                curses_main,
                logMod,
                config,
                (
                    WINDOW_MINH,
                    WINDOW_MINW,
                ),
                handler,
            )
        finally:
            logMod.flush()
