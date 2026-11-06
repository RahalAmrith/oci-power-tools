#########################################################################################
# Filename    : menu.py
# description : Numbered menu used to pick a section and a tool
#########################################################################################


def chooseFromMenu(title, names, exitLabel, drawScreen=None):
    """Returns the index of the chosen entry, or None when the user picks the exit entry.

    drawScreen is called before every redraw of the menu, so the menu appears on a clean page.
    """

    error = None

    while True:
        if drawScreen:
            drawScreen()

        print(f"\n{title}\n")

        for i, name in enumerate(names):
            print(f"\t{i+1:02d} : {name}")
        print(f"\t00 : {exitLabel}")

        if error:
            print(f"\n{error}")

        try:
            opt = int(input("\nEnter option number : "))
        except ValueError:
            error = "Error : Invalid option"
            continue

        if opt == 0:
            return None

        if 1 <= opt <= len(names):
            return opt - 1

        error = "Error : Invalid option"
