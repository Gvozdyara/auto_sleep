import logging
import tkinter as tk
from tkinter import ttk
from tkinter import font
from functools import partial
import threading
import time
from PIL import Image, ImageTk
import sys
import os

from observable import State, Variable
import funs


class App(tk.Tk):
    '''Main app '''

    def __init__(self):
        super().__init__()
        self.title("Auto sleep")
        self.geometry("250x100")
        try:
            ico = Image.open(os.path.join(
                os.path.split(sys.executable)[0], "icon.png"))
        except FileNotFoundError:
            ico = Image.open("icon.png")
        photo = ImageTk.PhotoImage(ico)
        self.wm_iconphoto(False, photo)

class TopBox(ttk.Frame):
    '''Frame for main information label '''

    def __init__(self, master: tk.Tk, text: tk.StringVar):
        super().__init__(master=master)
        font_ = font.Font(size=12, weight="bold")
        self.label = tk.Label(self, textvariable=text, font=font_, fg="#808080")
        self.build()

    def build(self):
        self.label.pack(ipady=5)


class InteractiveBox(ttk.Frame):
    '''A Frame to hold buttons'''

    def __init__(self, master: tk.Tk, sleep_state: Variable):
        super().__init__(master=master)
        self.sleep_btn = ttk.Button(self, text="В спящий режим",
                                    command=self.force_sleep, padding=2)
        self.check_btn = ttk.Checkbutton(self, text="Звук")
        self.sleep_state = sleep_state
        self.build()

    def force_sleep(self):
        logging.debug("Sleep btn is pressed")
        self.sleep_state.state.value = True

    def build(self):
        self.sleep_btn.pack(side=tk.BOTTOM, pady=(5, 5))
        # self.check_btn.pack()


class ViewMaster:
    '''An object to conrol main app'''

    def __init__(self, app: tk.Tk):
        self.main_label_text = tk.StringVar(app, value="Расчет времени...")
        self.main_label_text_var = Variable(self.on_main_label_text,
                                            self.main_label_text.get(),
                                            "Main label var")
        self.sleep_state_var = Variable(self.on_sleep_state, False,
                                        "Sleep state var")
        self.top_box = TopBox(app, self.main_label_text)
        self.interactive_box = InteractiveBox(app, self.sleep_state_var)
        self.build()
        self.main_program()

    def main_program(self):
        threading.Thread(target=funs.counter,
                         args=(self.main_label_text_var,), daemon=True).start()

    def on_sleep_state(self, value: bool, var: Variable):
        if not value:
            logging.debug(f'{var} value is not chenaged')
            return
        logging.debug(f'{var} is set to {value}. The computer is gonna sleep')
        var.state.value = False
        funs.force_sleep()

    def on_main_label_text(self, value: str, var: Variable, *args):
        # logging.debug((f'{var} is set to {value}. ',
        #                f'main label text will be changed'))
        self.main_label_text.set(value)

    def build(self):
        self.top_box.pack()
        self.interactive_box.pack(side=tk.BOTTOM)


