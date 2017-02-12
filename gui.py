# -*- coding: utf-8 -*-

import Tkinter as tk
import tkMessageBox
import dialog
import turnier2 as turnier

class WelcomeWindow(dialog.Dialog):
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
            self.gui.tur = turnier.load(self.gui)
            return 1
        except IOError:
            tkMessageBox.showwarning("IOError", "Kein gespeichertes Turnier vorhanden.")
            return 0

    def apply(self):
        self.gui.tur.continue_after_load()

    def new(self):
        self.withdraw()
        self.update_idletasks()

        self.gui.tur = turnier.Turnier(self.gui)

        self.cancel()

class GameNumberWindow(dialog.Dialog):
    def __init__(self, parent, gui, goodlist, waitlist, playlist, title="Beach with Friends"):
        self.goodlist = goodlist
        self.waitlist = waitlist
        self.playlist = playlist
        dialog.Dialog.__init__(self, parent, gui, title)

    def body(self, master):
        tk.Label(master, text="Anzahl zu spielender Spiele wählen.").pack()
        gridframe = tk.Frame(master)
        buttonlist = []
        tk.Label(gridframe, text="Normal:").grid(row=0)
        for gg, good in enumerate(self.goodlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(good), variable=self.gui.game_count, value=good))
            buttonlist[-1].grid(row=0, column=1+gg)
        tk.Label(gridframe, text="Rize wartet eins mehr:").grid(row=1)
        for ww, wait in enumerate(self.waitlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(wait), variable=self.gui.game_count, value=wait))
            buttonlist[-1].grid(row=1, column=1+ww)
        tk.Label(gridframe, text="Rize spielt eins mehr:").grid(row=2)
        for pp, play in enumerate(self.playlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(play), variable=self.gui.game_count, value=play))
            buttonlist[-1].grid(row=2, column=1+pp)
        gridframe.pack()
        return buttonlist[0]

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)

        box.pack()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("favicon.ico")
        self.root.title("Beach with Friends")
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

    def out_player_count(self, p):
        tkMessageBox.showinfo("Spieleranzahl", "Anzahl der Spieler: {}".format(p))

    def in_game_count(self, goodlist, waitlist, playlist):
        self.game_count = tk.IntVar()
        self.game_count.set(0)
        while self.game_count.get() == 0:
            self.selector = GameNumberWindow(self.root, self,goodlist, waitlist, playlist)
        return self.game_count.get()

GUI()