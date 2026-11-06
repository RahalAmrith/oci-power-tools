#########################################################################################
# Filename    : ui.py
# description : Startup banner and clean screen helpers shared by the menus
#########################################################################################

import os
import sys

APP_NAME = "OCI Power Tools"
TAGLINE = "Answer the questions the OCI Console and CLI can't"
AUTHOR = "Rahal Amrith"
REPO_URL = "https://github.com/RahalAmrith/oci-power-tools"

BANNER = [
    r"   ____  __________   ____                             ______            __    ",
    r"  / __ \/ ____/  _/  / __ \____ _      _____  _____   /_  __/___  ____  / /____",
    r" / / / / /    / /   / /_/ / __ \ | /| / / _ \/ ___/    / / / __ \/ __ \/ / ___/",
    r"/ /_/ / /____/ /   / ____/ /_/ / |/ |/ /  __/ /       / / / /_/ / /_/ / (__  ) ",
    r"\____/\____/___/  /_/    \____/|__/|__/\___/_/       /_/  \____/\____/_/____/  ",
]

RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


if os.name == "nt":
    # Running any command switches the Windows console to ANSI mode, so colors work
    os.system("")


def _isTerminal():
    return sys.stdout.isatty()


def _style(text, code):
    # Colors and screen clearing are skipped when the output is piped to a file or a test
    if _isTerminal() and "NO_COLOR" not in os.environ:
        return f"{code}{text}{RESET}"

    return text


def clearScreen():
    if not _isTerminal():
        return

    os.system("cls" if os.name == "nt" else "clear")


def printBanner():
    print("")

    for line in BANNER:
        print(_style(line, RED + BOLD))

    print(f"\n  {_style(TAGLINE, BOLD)}")
    print(f"  {_style(f'by {AUTHOR}  |  {REPO_URL}', DIM)}")


def printSessionBar(ctx):
    region = ctx.ocisdk.configs.get(ctx.profile, {}).get("region", "unknown")

    print(f"\n  Profile : {_style(ctx.profile, BOLD)}    Region : {_style(region, BOLD)}")


def showScreen(ctx=None, breadcrumb=None):
    """Clears the terminal and draws the banner, the session bar and the current location."""

    clearScreen()
    printBanner()

    if ctx is not None:
        printSessionBar(ctx)

    if breadcrumb:
        print(f"  Location: {breadcrumb}")

    print(_style("\n  " + "-" * 60, DIM))
