# -*- coding: utf-8 -*-

try:
    import Tkinter as tk
except:
    import tkinter as tk
try:
    import tkMessageBox
except:
    import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk
import time
import numpy as np
import dialog
import turnier2 as turnier

FILENAME = "players.txt"

class WelcomeWindow(dialog.Dialog):
    def header(self, master):
        imobj = Image.open("ims/logo-bg.png")
        dim = self.gui.dims_by_scale(0.1)[0]
        imobj = imobj.resize((dim, dim), Image.ANTIALIAS)
        self.gui.logo = ImageTk.PhotoImage(imobj)
        tk.Label(master, image=self.gui.logo, bg="#EDEEF3").pack()

    def body(self, master):
        tk.Label(master, text="Beachomize - Turniermanager", bg="#EDEEF3").pack()
        return None

    def buttonbox(self):
        box = tk.Frame(self, bg="#EDEEF3")

        w = tk.Button(box, text="Neu", width=10, command=self.new, default=tk.ACTIVE, bg="#EDEEF3")
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Laden", width=10, command=self.ok, bg="#EDEEF3")
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
        if self.gui.tur.state == 1:
            pass
        pass

    def new(self):
        self.withdraw()
        self.update_idletasks()

        names, mmr = self.gui.in_players()
        self.gui.tur = turnier.Turnier(names, mmr, display_mmr=True)

        self.cancel()

class GameNumberWindow(dialog.Dialog):
    def __init__(self, parent, gui, goodlist, waitlist, playlist, title="Beach with Friends"):
        self.goodlist = goodlist
        self.waitlist = waitlist
        self.playlist = playlist
        dialog.Dialog.__init__(self, parent, gui, title)

    def header(self, master):
        imobj = Image.open("ims/logo-bg.png")
        dim = self.gui.dims_by_scale(0.1)[0]
        imobj = imobj.resize((dim, dim), Image.ANTIALIAS)
        self.gui.logo = ImageTk.PhotoImage(imobj)
        tk.Label(master, image=self.gui.logo, bg="#EDEEF3").pack()

    def body(self, master):
        tk.Label(master, text="Anzahl zu spielender Spiele wählen.", bg="#EDEEF3").pack()
        gridframe = tk.Frame(master, bg="#EDEEF3")
        buttonlist = []
        tk.Label(gridframe, text="Normal:", bg="#EDEEF3").grid(row=0)
        for gg, good in enumerate(self.goodlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(good), variable=self.gui.game_count, value=good, bg="#EDEEF3"))
            buttonlist[-1].grid(row=0, column=1+gg)
        tk.Label(gridframe, text="Rize wartet eins mehr:", bg="#EDEEF3").grid(row=1)
        for ww, wait in enumerate(self.waitlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(wait), variable=self.gui.game_count, value=wait, bg="#EDEEF3"))
            buttonlist[-1].grid(row=1, column=1+ww)
        tk.Label(gridframe, text="Rize spielt eins mehr:", bg="#EDEEF3").grid(row=2)
        for pp, play in enumerate(self.playlist):
            buttonlist.append(tk.Radiobutton(gridframe, text=str(play), variable=self.gui.game_count, value=play, bg="#EDEEF3"))
            buttonlist[-1].grid(row=2, column=1+pp)
        gridframe.pack()
        return buttonlist[0]

    def buttonbox(self):
        box = tk.Frame(self, bg="#EDEEF3")

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE, bg="#EDEEF3")
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)

        box.pack()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass
        self.root.title("Beach with Friends")
        self.root.configure(bg="#EDEEF3")
        self.screen_resolution = [self.root.winfo_screenwidth(), self.root.winfo_screenheight()]
        self.tur = None

        # self.root.withdraw()
        self.welcome = WelcomeWindow(self.root, self)
        if self.tur is not None:
            # self.root.deiconify()
            self.tur.set_game_count(self.in_game_count())

            #create main window elements here
            #banner
            imobj = Image.open("ims/banner2.jpg")
            dim = self.dims_by_scale(0.3)[0]
            fac = float(dim) / imobj.size[0]
            dim2 = int(imobj.size[1] * fac)
            imobj = imobj.resize((dim, dim2), Image.ANTIALIAS)
            self.banner = ImageTk.PhotoImage(imobj)
            tk.Label(self.root, image=self.banner, bg="#EDEEF3").grid(columnspan=3)

            #clock
            clock = tk.Label(self.root, font=('times', 20, 'bold'), bg="#EDEEF3")
            clock.grid(row=1, column=1, padx=10, pady=10)
            def tick():
                s = time.strftime('%H:%M:%S')
                if s != clock["text"]:
                    clock["text"] = s
                clock.after(200, tick)
            tick()

            MAXROWS = 10

            #player list
            tk.Label(self.root, text="Spielerliste:", font=('times', 12, 'bold'), bg="#EDEEF3").grid(row=2,column=0)
            self.pl_table=tk.Frame(self.root, bg="#EDEEF3")
            self.pl_labels = []
            for id, nam in enumerate(self.tur.players.name):
                self.pl_labels.append(tk.Label(self.pl_table, text=nam, bg="#EDEEF3"))
                self.pl_labels[id].grid(row=id%MAXROWS, column=int(id/MAXROWS), ipadx = 5)
            self.pl_table.grid(row=3,column=0)

            #schedule
            tk.Label(self.root, text="Zeitplan:", font=('times', 12, 'bold'), bg="#EDEEF3").grid(row=2,column=1)
            self.schedule_table = tk.Frame(self.root, bg="#EDEEF3")
            self.schedule_labels = []
            for id, tim in enumerate(self.tur.schedule):
                hour = int(tim/100)
                minute = tim-hour*100
                self.schedule_labels.append(tk.Label(self.schedule_table, text="{:02d} - {:02d}:{:02d}".format(id+1, hour, minute), bg="#EDEEF3"))
                self.schedule_labels[id].grid(row=id%MAXROWS, column=int(id/MAXROWS), ipadx = 5)
            self.schedule_labels[0]["fg"] = "dark green"
            self.schedule_table.grid(row=3,column=1)

            #game announcement
            tk.Label(self.root, text="Aktuelles Spiel:", font=('times', 12, 'bold'), bg="#EDEEF3").grid(row=2,column=2)
            self.game_table = tk.Frame(self.root, bg="#EDEEF3")
            self.game_labels = []
            if self.tur.display_mmr:
                self.mmr_labels = []
            for ci in range(self.tur.c):
                if ci == 0:
                    tk.Label(self.game_table, text="Center Court:", font="-size 9 -weight bold", bg="#EDEEF3").pack()
                else:
                    tk.Label(self.game_table, text="Feld {}:".format(ci), font="-size 9 -weight bold", bg="#EDEEF3").pack()
                self.game_labels.append(tk.Label(self.game_table, text="", bg="#EDEEF3"))
                self.game_labels[ci].pack()
                if self.tur.display_mmr:
                    self.mmr_labels.append(tk.Label(self.game_table, text="", bg="#EDEEF3"))
                    self.mmr_labels[ci].pack()
            self.game_table.grid(row=3,column=2)

            #buttons
            buttonbox = tk.Frame(self.root, bg="#EDEEF3")
            self.wait_but = tk.Button(buttonbox, text="Pausenwunsch", command=self.wait_request, bg="#EDEEF3")
            self.wait_but.pack(side=tk.LEFT, padx=5, pady=5)
            self.wait_request = None
            self.game_but = tk.Button(buttonbox, text="Nächstes Spiel", default=tk.ACTIVE, command=self.new_game, bg="#EDEEF3")
            self.game_but.pack(side=tk.LEFT, padx=5, pady=5)
            self.result_but = tk.Button(buttonbox, text="Ergebnis eintragen", command=self.enter_results, state=tk.DISABLED, bg="#EDEEF3")
            self.result_but.pack(side=tk.LEFT, padx=5, pady=5)
            self.stats_but = tk.Button(buttonbox, text="Punktestände", command=self.show_stats, bg="#EDEEF3")
            self.stats_but.pack(side=tk.LEFT, padx=5, pady=5)
            buttonbox.grid(row=4, columnspan=3, padx=5, pady=5)

            #properties
            propbox = tk.Frame(self.root, bg="#EDEEF3")
            tk.Label(propbox, text=" Anzahl Spieler: {}  |".format(self.tur.p), bg="#EDEEF3").grid(row=0, column=0)
            tk.Label(propbox, text=" Anzahl Courts: {}  |".format(self.tur.c), bg="#EDEEF3").grid(row=0, column=1)
            tk.Label(propbox, text=" Wartespieler: {}  |".format(self.tur.w), bg="#EDEEF3").grid(row=0, column=2)
            tk.Label(propbox, text=" Rizemode: {}  ".format(self.tur.rizemode), bg="#EDEEF3").grid(row=0, column=3)
            propbox.grid(row=5, columnspan=3)

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

    def in_game_count(self):
        self.game_count = tk.IntVar()
        self.game_count.set(0)
        while self.game_count.get() == 0:
            # self.root.withdraw()
            self.selector = GameNumberWindow(self.root, self, self.tur.goodlist, self.tur.waitlist, self.tur.playlist)
            # self.root.deiconify()
        return self.game_count.get()

    def in_players(self):
        filename = FILENAME
        with open(filename) as f:
            filecontent = f.readlines()
        names = []
        init_mmr = []
        for st in filecontent:
            spl = st.split()
            names.append(spl[0])
            init_mmr.append(int(spl[1]))
        return names, init_mmr

    def wait_request(self):
        pass

    def new_game(self):
        self.tur.game(self.wait_request)
        team_indices = self.tur.games[-1]
        names_sorted = self.tur.players.name[team_indices]
        if self.tur.display_mmr:
            mmr_sorted = self.tur.players.mmr[team_indices]
            mmr_mean = np.mean(mmr_sorted.astype(float), axis=1)
        for i in range(len(team_indices)/2):
            self.game_labels[i]["text"] = names_sorted[2*i][0] + "/" + names_sorted[2*i][1] + " - " + names_sorted[2*i+1][0] + "/" + names_sorted[2*i+1][1]
            self.mmr_labels[i]["text"] = str(mmr_sorted[2 * i][0]) + "/" + str(mmr_sorted[2 * i][1]) + " (ø" + str(mmr_mean[i]) + ") - " + str(mmr_sorted[2 * i][0]) + "/" + str(mmr_sorted[2 * i][1]) + " (ø" + str(mmr_mean[i]) + ")"
        self.game_but["state"] = tk.DISABLED
        self.result_but["state"] = tk.ACTIVE
        for ii in range(self.tur.i-1):
            self.schedule_labels[ii]["fg"] = "red"
        self.schedule_labels[self.tur.i-1]["fg"] = "dark green"
        self.schedule_labels[self.tur.i - 1]["font"] = "-size 9 -weight bold"

    def enter_results(self):
        pass

    def show_stats(self):
        pass

if __name__ == '__main__':
    GUI()