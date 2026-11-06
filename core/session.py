#########################################################################################
# Filename    : session.py
# description : Startup logic - config file, required directories and profile selection
#########################################################################################

import os
import sys
from dataclasses import dataclass

from helpers.ocisdk import OCISDK
from helpers.utils import getProfilesFromConfig


@dataclass
class Session:
    ocisdk: OCISDK
    profile: str


def askConfigPathInTerminal():
    try:
        path = input("Enter the path to your OCI config file : ").strip()
    except EOFError:
        return None

    return os.path.expanduser(path) if path else None


def pickConfigFile():
    """Opens a file picker, or asks in the terminal when there is no GUI to show it on."""

    try:
        # Imported here because easygui needs tkinter, which a CLI only machine may not have
        import easygui

        return easygui.fileopenbox()

    except Exception:
        print("No file picker available on this machine.")
        return askConfigPathInTerminal()


def startSession():
    defaultConfigFile = os.path.expanduser("~/.oci/config")

    if os.path.exists(defaultConfigFile):
        configPath = defaultConfigFile
    else:
        configPath = pickConfigFile()

    if configPath and not os.path.isfile(configPath):
        print(f"Error: Config file not found : {configPath}")
        sys.exit()

    if not configPath:
        print("Error: No config file selected.")
        sys.exit()

    print(f"Using config file : {configPath}")

    ocisdk = OCISDK(config_file_path=configPath)

    if not os.path.exists("reports"):
        print("Creating Directory : reports")
        os.makedirs("reports")

    try:
        profiles = getProfilesFromConfig(configPath)
        selectedProfile = profiles[0]

    except Exception:
        print("Error: Cannot read config file or empty config file.")
        sys.exit()

    if len(profiles) > 1:
        print("Please select config name : \n")

        for i, prof in enumerate(profiles):
            print(f"\t{i+1} : {prof}")

        try:
            ind = int(input("\nEnter the profile number : "))
            selectedProfile = profiles[ind - 1]
        except Exception:
            print("Error : Invalid input")

    print(f"Selected Profile : {selectedProfile}")

    return Session(ocisdk=ocisdk, profile=selectedProfile)
