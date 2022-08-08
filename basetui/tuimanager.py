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
    """The central runtime function.

    Args:
        stdscr (_curses.window): the window object
        colorinfo (dict): the dict containing colordefaults and pairs
        boxchars (dict): the dict containing preferred box characters
        logMod (logbuf): the logger object already set up for autoflushing
        windim (Tuple[int]): the minimum allowed window dimensions
        handler (callable): the function, method, or (most commonly) bound method to call with input strings. Check documentation for details on the signature of this function.
    """

    # Define a logfunc, the buffer, and shortcuts to some colors
    logfunc = lambda t, p=2: logMod.log(f"SUBMAIN -> {t}", p)
    buf = ""
    COLORSMAIN = colorinfo["defaults"]["main"]
    COLORSALERT = colorinfo["defaults"]["alert"]
    COLORSSTATUSBAR = colorinfo["defaults"]["status"]
    logfunc("Setup complete", 0)

    # Perform screen initialization
    szwarn, nrow, ncol = showsizewarn(stdscr, COLORSMAIN, windim)
    supd(stdscr, "", ncol, COLORSSTATUSBAR, COLORSSTATUSBAR)
    addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
    stdscr.addstr(nrow - 2, 0, boxchars["HORIZ"] * ncol, COLORSMAIN)
    logfunc("Screen initialized", 0)

    # Iter until break
    while True:
        # Try to get input
        try:
            # if no input given in (`Curses Setup/halfdelay` in config file) tenths of a second, raises a _curses.error.
            inp = stdscr.getkey()
        except _curses.error:
            inp = None

        # If resized, check against windim & possibly display warning
        if inp == "KEY_RESIZE":
            # Temp store then check & reload
            o_szwarn = bool(szwarn)
            szwarn, nrow, ncol = showsizewarn(stdscr, COLORSMAIN, windim)
            logfunc(f"Resize detected, new size is {nrow}x{ncol}", 0)

            # Redraw if it was not acceptable but is now
            if szwarn is True and o_szwarn is False:
                stdscr.clear()
                addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
                stdscr.addstr(nrow - 2, 0, boxchars["HORIZ"] * ncol, COLORSMAIN)
                supd(stdscr, " " * ncol, ncol, COLORSSTATUSBAR, COLORSSTATUSBAR)

            del o_szwarn  # del temp var

        # If acceptable size and we got a str and it was len 1, switch on it.
        #   - Len of 1 bars arrow keys
        if szwarn is False and isinstance(inp, str) and len(inp) == 1:
            # clear the status bar
            supd(stdscr, " " * ncol, ncol, COLORSSTATUSBAR, COLORSSTATUSBAR)

            # If enter was pressed, handle input
            if inp == curses.KEY_ENTER or ord(inp) == 10:
                # Debug/log it
                logfunc(f"Enter pressed with buffer `{buf}`", 0)

                # break if want to quit
                if buf in ["exit", "quit"]:
                    break

                # display the flashy red test message if desired
                elif buf == "test":
                    supd(
                        stdscr,
                        f"This is a test message!",
                        ncol,
                        COLORSALERT | curses.A_BLINK | curses.A_BOLD,
                        COLORSSTATUSBAR,
                    )

                # hand it off to the provided handler function otherwise
                else:
                    handler(stdscr, colorinfo, logMod, buf)

                # reset buffer & cursor
                buf = ""
                addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)

            # if backspace, remove the last character from buffer & redraw
            elif inp == curses.KEY_BACKSPACE or ord(inp) == 127:
                if len(buf) > 0:
                    buf = buf[: len(buf) - 1]
                    addcursor(stdscr, buf, ncol, nrow, COLORSMAIN, COLORSSTATUSBAR)
                    stdscr.refresh()

            # if any other acceptable character (already verified to be len 1), add to
            #   buffer iff we wouldn't be writing off of the screen.
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

            # this key has not been handled, alert the user to that fact.
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


def showsizewarn(
    stdscr: _curses.window, style, windim: Tuple[int]
) -> Tuple[bool, int, int]:
    """Shows a size warning if the window is too small.

    Args:
        stdscr (_curses.window): the window object
        style (int): the color pair id to use for the size warning
        windim (Tuple[int]): the minimum dimensions of the window as specified in config file

    Returns:
        Tuple[bool, int, int]: (a) if size is acceptable, (b) line count, (c) col count
    """
    curses.update_lines_cols()
    if curses.LINES < windim[0] or curses.COLS < windim[1]:
        stdscr.clear()
        stdscr.addstr(
            3,
            0,
            f"Size is {curses.LINES}x{curses.COLS}, must be at least {windim[0]}x{windim[1]} to properly use this application!",
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
    """Controls the status bar (first line); this is used to display status messages to the user.

    Args:
        stdscr (_curses.window): the window object
        string (str): the string to display
        ncol (int): the number of columns
        style (int): the color pair id to use as style for the text
        sbarstyle (int): the color pair id to use as style for areas not covered with text provided
    """
    sts = string[:ncol]
    stdscr.addstr(0, 0, " " * ncol, sbarstyle)
    stdscr.refresh()
    stdscr.addstr(0, max(int(ncol / 2) - int(len(sts) / 2), 0), sts, style)
    stdscr.refresh()


def addcursor(stdscr: _curses.window, buff, ncol, nrow, style, sbarstyle):
    """Adds current input, plus buffer, to last line.

    Args:
        stdscr (_curses.window): The window object
        buff (str): The current buffer
        ncol (int): the number of columns
        nrow (int): the number of lines
        style (int): the color pair id to use as style
        sbarstyle (int): the color pair id to use in the status bar, if need be
    """
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
    #########
    # COLORS

    # Init Colors
    for k in [x for x in config.sections() if x.startswith("Color Definition ")]:
        ccf = config[k]
        ccfg = [int(ccf[x]) for x in ["num", "r", "g", "b"]]
        logMod.log(
            f"Creating color: {ccfg}",
            priority=1,
        )
        curses.init_color(*ccfg)

    # Init Color Pairs
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

    # Init Color Defaults & Presets
    colordefaults = {}
    ccf = config["Color Defaults"]
    for k in ccf:
        colordefaults[k] = curses.color_pair(int(ccf[k]))
    if not len({"alert", "main", "status"} - set(ccf.keys())) == 0:
        raise ValueError("Expected all of alert, main, status in color defaults")

    # Compose Colors
    colorinfo = {"defaults": colordefaults, "pairs": colorpairs}
    logMod.log("Loaded colors", priority=1)

    ######################
    # OTHER INITALIZATION

    # Box Chars
    boxchars = {"HORIZ": "─", "VERTI": "│"}
    logMod.log("Loaded boxchars", priority=1)

    ################
    # CURSES CONFIG

    # Halfdelay controls how long stdscr.getkey() will wait before throwing a
    #   _curses.error. If not set, your CPU usage will max out
    halfdelay_amt = int(config["Curses Setup"]["halfdelay"])
    curses.halfdelay(halfdelay_amt)
    logMod.log(
        f"Loaded keypress exception delay as {halfdelay_amt/10:.1f}s", priority=1
    )

    ##############
    # RUN SUBMAIN

    # set cursor to invisible, then back again afterwards
    curses.curs_set(0)
    try:
        submain(stdscr, colorinfo, boxchars, logMod, windim, handler)
    finally:
        curses.curs_set(1)
