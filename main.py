# ctypes required for using GetTickCount64()
import ctypes
import datetime as dt
from functools import partial
import logging
import os
import re
import subprocess
import time
import sys
from threading import Thread
from gui import App, ViewMaster
from pystray import MenuItem as item
import pystray
from PIL import Image



def quit_window(icon, item):
    icon.stop()
    root.destroy()


def show_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)


def withdraw_window():
    root.withdraw()
    try:
        image = Image.open(os.path.join(
            os.path.split(sys.executable)[0], "icon.png"))
    except FileNotFoundError:
        image = Image.open("icon.png")
    menu = (item('Quit', quit_window), item('Show', show_window))
    icon = pystray.Icon("name", image, "Auto sleep", menu)
    icon.run()


def main():
    global root
    formatter = '[%(levelname)s] [%(funcName)s] [%(asctime)s] %(message)s'
    logging.basicConfig(filename="error.log",
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format=formatter)
    root = App()
    ViewMaster(root)

    root.protocol('WM_DELETE_WINDOW', withdraw_window)
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f'on main {e}')



