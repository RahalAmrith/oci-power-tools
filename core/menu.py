#########################################################################################
# Filename    : menu.py
# description : Numbered menu used to pick a section and a tool
#########################################################################################


def chooseFromMenu(title, names, exitLabel):
    """Returns the index of the chosen entry, or None when the user picks the exit entry."""

    while True:
        print(f"\n{title}\n")

        for i, name in enumerate(names):
            print(f"\t{i+1:02d} : {name}")
        print(f"\t00 : {exitLabel}")

        try:
            opt = int(input("\nEnter option number : "))
        except ValueError:
            print("Error : Invalid option")
            continue

        if opt == 0:
            return None

        if 1 <= opt <= len(names):
            return opt - 1

        print("Error : Invalid option")
