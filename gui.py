# -*- coding: utf-8 -*-

import Tkinter as Tk

import turnier2 as turnier

class GUI:
    def __init__(self):
        self.root = Tk.Tk()
        self.welcome = Tk.Toplevel()
        self.welcome.title("Beach with Friends")
        Tk.Message(self.welcome, text="Beach with Friends - Turniermanager").pack()
        Tk.Button(self.welcome, text="START", command=self.start_button_press).pack()

        self.root.withdraw()
        self.root.mainloop()

    def start_button_press(self):
        self.welcome.destroy()
        turnier.Turnier(self)

    def out_player_count(self, p):
        player_count_output = Tk.Toplevel()
        player_count_output.title("Greetings")
        Tk.Message(player_count_output, text="Anzahl der Spieler: {}".format(p)).pack()
        Tk.Button(player_count_output, text="OK", command=player_count_output.destroy).pack()

GUI()