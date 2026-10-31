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
from tools import SECTIONS

ctx = startSession()

print("Select option to continue :")

while True:
    sectionIdx = chooseFromMenu(
        "Select a section :", [s.SECTION_NAME for s in SECTIONS], "Exit"
    )

    if sectionIdx is None:
        break

    section = SECTIONS[sectionIdx]
    tools = section.getTools()

    toolIdx = chooseFromMenu(
        f"====== {section.SECTION_NAME}", [name for name, _ in tools], "Back"
    )

    if toolIdx is not None:
        runTool(tools[toolIdx][1], ctx)
        break

input("\nPress Enter to exit ...")
