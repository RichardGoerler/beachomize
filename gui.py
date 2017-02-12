# -*- coding: utf-8 -*-

import Tkinter as tk
import tkMessageBox
import dialog
import turnier2 as turnier


class MyDialog(dialog.Dialog):

    def body(self, master):

        tk.Label(master, text="First:").grid(row=0)
        tk.Label(master, text="Second:").grid(row=1)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1  # initial focus

    def validate(self):
        try:
            first = int(self.e1.get())
            second = int(self.e2.get())
            self.result = first, second
            return 1
        except ValueError:
            tkMessageBox.showwarning(
                "Bad input",
                "Illegal values, please try again"
            )
            return 0

    def apply(self):
        print(self.result)  # or something

class WelcomeWindow(dialog.Dialog):
    def __init__(self, parent, gui, title=None):
        self.gui = gui
        dialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        tk.Label(master, text="Beach with Friends - Turniermanager").grid(row=0)
        return None

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text="Neu", width=10, command=self.new, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Laden", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def validate(self):
        try:
            self.parent.tur = turnier.load(self.gui)
        except IOError:
            tkMessageBox.showwarning("IOError", "Kein gespeichertes Turnier vorhanden.")
            return 0

    def apply(self):
        self.tur.continue_after_load()

    def new(self):
        self.withdraw()
        self.update_idletasks()

        self.parent.tur = turnier.Turnier(self.gui)

        self.cancel()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.screen_resolution = [self.root.winfo_screenwidth(), self.root.winfo_screenheight()]
        self.tur = None

        self.welcome = WelcomeWindow(self.root, self)
        if self.tur is not None:
            #self.root.withdraw()
            self.root.mainloop()

    def dims_by_scale(self, scale):
        if hasattr(scale, '__iter__'):
            return [int(el * sc) for el, sc in zip(self.screen_resolution,scale)]
        return [int(el * scale) for el in self.screen_resolution]

    def center_coords(self, window_dims):
        posX = int((self.screen_resolution[0] - window_dims[0]) / 2)
        posY = int((self.screen_resolution[1] - window_dims[1]) / 2)
        return [posX, posY]

    def welcome_message(self):
        tkMessageBox.showinfo("Greetings","Beach with Friends - Turniermanager")

    def out_player_count(self, p):
        tkMessageBox.showinfo("Spieleranzahl", "Anzahl der Spieler: {}".format(p))

GUI()