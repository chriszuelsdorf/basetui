import curses, _curses
import configparser
import string
from typing import Tuple

from .logmod import logbuf


def submain(
    stdscr: _curses.window,
    colorinfo: dict,
    boxchars,
    logMod: logbuf,
    windim: Tuple[int],
    handler: callable,
) -> None:
    logfunc = lambda t, p=2: logMod.log(f"SUBMAIN -> {t}", p)
    buf = ""
    COLORSMAIN = colorinfo["defaults"]["main"]
    COLORSALERT = colorinfo["defaults"]["alert"]
    COLORSSTATUSBAR = colorinfo["defaults"]["status"]
    logfunc("Initialized color constants", 0)
    szwarn, nrow, ncol = showsizewarn(stdscr, COLORSMAIN, windim)
    supd(stdscr, "", ncol, COLORSSTATUSBAR, COLORSSTATUSBAR)
    addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
    stdscr.addstr(nrow - 2, 0, boxchars["HORIZ"] * ncol, COLORSMAIN)
    logfunc("Basic layout drawn", 0)
    while True:
        try:
            inp = stdscr.getkey()
        except _curses.error:
            inp = None
        if inp == "KEY_RESIZE":
            logfunc("Resize detected", 0)
            szwarn, nrow, ncol = showsizewarn(stdscr, COLORSMAIN, windim)
        if szwarn is False and isinstance(inp, str) and len(inp) == 1:
            supd(stdscr, " " * ncol, ncol, COLORSSTATUSBAR, COLORSSTATUSBAR)
            if inp == curses.KEY_ENTER or ord(inp) == 10:
                logfunc(f"Enter pressed with buffer `{buf}`", 0)
                if buf in ["exit", "quit"]:
                    break
                elif buf == "test":
                    supd(
                        stdscr,
                        f"This is a test message!",
                        ncol,
                        COLORSALERT | curses.A_BLINK | curses.A_BOLD,
                        COLORSSTATUSBAR,
                    )
                else:
                    handler(stdscr, colorinfo, logMod, buf)
                buf = ""
                addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
            elif inp == curses.KEY_BACKSPACE or ord(inp) == 127:
                if len(buf) > 0:
                    buf = buf[: len(buf) - 1]
                    addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
                    stdscr.refresh()
            elif inp in string.ascii_letters + string.digits + string.punctuation + " ":
                if len(buf) < ncol - 6:
                    buf += inp
                    addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
                else:
                    supd(
                        stdscr,
                        "Attemped to exceed max input length!",
                        ncol,
                        COLORSALERT | curses.A_BLINK | curses.A_BOLD,
                        COLORSSTATUSBAR,
                    )
            else:
                supd(
                    stdscr,
                    f"Non-accepted key `{inp}`",
                    ncol,
                    COLORSALERT | curses.A_BLINK | curses.A_BOLD,
                    COLORSSTATUSBAR,
                )


def get_row_col():
    """Gets rows & columns

    Returns:
        Tuple[int]: (rows, columns)
    """
    curses.update_lines_cols()
    return curses.LINES, curses.COLS


def showsizewarn(stdscr: _curses.window, style, windim: Tuple[int]):
    curses.update_lines_cols()
    if curses.LINES < windim[0] or curses.COLS < windim[1]:
        stdscr.clear()
        stdscr.addstr(
            3,
            0,
            f"Size is {curses.LINES}x{curses.COLS}, must be at least {windim[0]}x{windim[1]} to properly use planodoro!",
            style | curses.A_BLINK,
        )
        stdscr.refresh()
    else:
        stdscr.addstr(0, 12, " " * (curses.COLS - 12))
    return (
        curses.LINES < windim[0] or curses.COLS < windim[1],
        curses.LINES,
        curses.COLS,
    )


def supd(stdscr: _curses.window, string, ncol, style, sbarstyle):
    # this has custody of line 1 cols 8 to -10 but must include 4 chars of padding before & after
    sts = string[:ncol]
    stdscr.addstr(0, 0, " " * ncol, sbarstyle)
    stdscr.refresh()
    stdscr.addstr(0, max(int(ncol / 2) - int(len(sts) / 2), 0), sts, style)
    stdscr.refresh()


def addcursor(stdscr: _curses.window, buff, ncol, nrow, style, sbarstyle):
    toadd = ">>> " + buff + (" " * (ncol - 5 - len(buff)))
    if len(toadd) >= ncol:
        supd(stdscr, "Max character length exceeded!", ncol, style, sbarstyle)
    else:
        stdscr.addstr(nrow - 1, 0, toadd, style)
        stdscr.addstr(nrow - 1, len(buff) + 4, "_", style | curses.A_BLINK)
        stdscr.refresh()


def curses_main(
    stdscr: _curses.window,
    logMod: logbuf,
    config: configparser.ConfigParser,
    windim: Tuple[int],
    handler: callable,
):
    # Init Colors themselves
    for k in [x for x in config.sections() if x.startswith("Color Definition ")]:
        ccf = config[k]
        logMod.log(
            f"Creating color: {[int(ccf[x]) for x in ['num', 'r', 'g', 'b']]}",
            priority=1,
        )
        curses.init_color(*[int(ccf[x]) for x in ["num", "r", "g", "b"]])
    # Color pairs
    colorpairs = {}
    for k in [x for x in config.sections() if x.startswith("Color Pair ")]:
        ccf = config[k]
        nm = int(ccf["num"])
        fg = ccf["fg"]
        fg = int(fg) if fg.isnumeric() else getattr(curses, fg)
        bg = ccf["bg"]
        bg = int(bg) if bg.isnumeric() else getattr(curses, bg)
        logMod.log(
            f"Creating color pair: {[ccf['num'], ccf['fg'], ccf['bg']]} -> {[nm, fg, bg]}",
            priority=1,
        )
        curses.init_pair(nm, fg, bg)
        colorpairs[nm] = curses.color_pair(nm)
    # Colors
    # curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    # COLORPAIR_YELLOW_BLACK = curses.color_pair(1)
    # curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    # COLORPAIR_WHITE_RED = curses.color_pair(2)
    # curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    # COLORPAIR_YELLOW_BLUE = curses.color_pair(3)
    # colorpairs = {
    #     "COLORPAIR_YELLOW_BLACK": COLORPAIR_YELLOW_BLACK,
    #     "COLORPAIR_WHITE_RED": COLORPAIR_WHITE_RED,
    #     "COLORPAIR_YELLOW_BLUE": COLORPAIR_YELLOW_BLUE,
    # }
    colordefaults = {}
    ccf = config["Color Defaults"]
    for k in ccf:
        colordefaults[k] = curses.color_pair(int(ccf[k]))
    if not len({"alert", "main", "status"} - set(ccf.keys())) == 0:
        raise ValueError("Expected all of alert, main, status in color defaults")
    # colordefaults = {
    #     "main": COLORPAIR_YELLOW_BLACK,
    #     "status": COLORPAIR_YELLOW_BLUE,
    #     "alert": COLORPAIR_WHITE_RED,
    # }
    colorinfo = {"defaults": colordefaults, "pairs": colorpairs}
    logMod.log("Loaded colors", priority=1)

    # Box Chars
    boxchars = {"HORIZ": "─", "VERTI": "│"}
    logMod.log("Loaded boxchars", priority=1)

    # Curses setup
    halfdelay_amt = int(config["Curses Setup"]["halfdelay"])
    curses.halfdelay(halfdelay_amt)
    curses.curs_set(0)
    logMod.log(
        f"Loaded keypress exception delay as {halfdelay_amt/10:.1f}s", priority=1
    )
    try:
        submain(stdscr, colorinfo, boxchars, logMod, windim, handler)
        # curses.init_pair(25, curses.COLOR_WHITE, curses.COLOR_RED)
        # tcolor_alert = curses.color_pair(25)
        # stdscr.clear()
        # stdscr.addstr(0, 0, "This is test text!", tcolor_alert | curses.A_BLINK)
        # stdscr.refresh()
        # sleep(5)
    finally:
        curses.curs_set(1)
