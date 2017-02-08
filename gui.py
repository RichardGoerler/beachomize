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


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.screen_resolution = [self.root.winfo_screenwidth(), self.root.winfo_screenheight()]
        #self.welcome = tk.Toplevel()
        #welcome_dims = self.dims_by_scale([0.15,0.3])
        #welcome_coords = self.center_coords(welcome_dims)
        #self.welcome.geometry("{}x{}+{}+{}".format(welcome_dims[0], welcome_dims[1], welcome_coords[0], welcome_coords[1]))
        #self.welcome.title("Beach with Friends")
        #tk.Message(self.welcome, text="Beach with Friends - Turniermanager", width=200).pack()
        #tk.Button(self.welcome, text="START", command=self.start_button_press).pack()

        self.welcome_message()
        self.test = MyDialog(self.root, "Dies ist ein Test")
        turnier.Turnier(self)

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