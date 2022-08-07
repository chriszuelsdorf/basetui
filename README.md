# basetui - Python curses/ncurses abstraction

## What is it?

If you've ever used Python's `curses` package, you'll know it can be a bear to manage input, logging, and properly closing the curses session. Basetui seeks to abstract away what you don't need to have control over, to make development much faster.

## Main Features
Here are a few of the features incorporated.
- Status bar and input handling
- Built-in basic logging
- Color customization

## How to Install
Use pip to install directly from Github:

```sh
python3 -m pip install git+https://github.com/chriszuelsdorf/basetui
```

## How to use

A short example:
```py3
import curses
import basetui

# You only need to import _curses for the typehinting.
import _curses


# This callable signature is required precisely.
# - stdscr - used for adding text to the screen, or as below passing to functions which do that for you.
# - colorinfo - contains guaranteed defaults as well as any custom pairs defined
# - logMod - basetui's built-in logger; use it with the `.log(x)` method
# - buf - the string input by the user
def handler(stdscr: _curses.window, colorinfo: dict, logMod: basetui.logbuf, buf: str):
    logMod.log("See me in the logs!")
    # basetui provides supd to update the status bar; it requires the string, number of columns,
    #   and the styling for the alert itself, as well as for the rest of the status bar.
    basetui.supd(
        stdscr,
        f"You typed {buf[:40]}",
        basetui.get_row_col()[1],
        colorinfo["defaults"]["alert"] | curses.A_BLINK | curses.A_BOLD,
        colorinfo["defaults"]["status"],
    )


if __name__ == "__main__":
    # Once you've defined your callable, start the tui with a call to basetui.basetui; you need
    #   - the base directory
    #       - This should contain config.ini, and any folders for the path to the `Startup/logfile` 
    #           path template specified in config.ini.
    #   - your handler callable
    basetui.basetui(
        "/Users/christopherzuelsdorf/dev/learn-lang/py3/proj04_fincli/pfcli2", handler
    )

```