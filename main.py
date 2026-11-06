#########################################################################################
# Filename    : main.py
# Fi1eType    : Python Source file
# Author      : Rahal Amrith
# Created on  : 13/10/2022
# description : Main entry point of the program
#########################################################################################

import warnings

warnings.filterwarnings("ignore")

from core.menu import chooseFromMenu
from core.runner import runTool
from core.session import startSession
from core.ui import printBanner, showScreen
from tools import SECTIONS

printBanner()
print("\n  Starting up ...\n")

ctx = startSession()

while True:
    sectionIdx = chooseFromMenu(
        "Select a section :",
        [s.SECTION_NAME for s in SECTIONS],
        "Exit",
        drawScreen=lambda: showScreen(ctx, "Home"),
    )

    if sectionIdx is None:
        break

    section = SECTIONS[sectionIdx]
    tools = section.getTools()

    toolIdx = chooseFromMenu(
        f"====== {section.SECTION_NAME}",
        [name for name, _ in tools],
        "Back",
        drawScreen=lambda: showScreen(ctx, f"Home > {section.SECTION_NAME}"),
    )

    if toolIdx is not None:
        toolName, tool = tools[toolIdx]

        showScreen(ctx, f"Home > {section.SECTION_NAME} > {toolName}")
        runTool(tool, ctx)
        break

input("\nPress Enter to exit ...")
