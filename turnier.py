# -*- coding: utf-8 -*-

import numpy as np
import pdb

FILENAME = "players.txt"

IND = 0
WON = 1
DIF = 2
POI = 3
POI_OPP = 4
MMR = 5
WAI = 6

def calc_game_count(P, W):
    waitlist = []
    playlist = []
    goodlist = []
    f = W    #player position in round waiting queue
    i = 1    #number of games played
    r = 2    #number of waiting rounds to test (when 1, calculation is aborted the first time f is zero)
    while not r == 0:
        if P == f+1:    #if one player (me) can play a game more to make it work
            playlist.append(i)
        if f == 1:      #if one player (me) can wait a game more
            waitlist.append(i)
        if f == 0:      #if it works regularly
            goodlist.append(i)
            r-=1
        f += W
        f %= P
        i += 1
    return goodlist, waitlist, playlist

def lcm1(f):
    ff = f
    while not ff == int(ff):
        ff += f
    return int(ff)

def split_result(str):
    res = [int(i3) for j3 in [s3.split() for s3 in [i2 for j2 in [s2.split('-') for s2 in [i1 for j1 in
                [s1.split(',') for s1 in str.split('/')] for i1 in j1]] for i2 in j2]] for i3 in j3 if i3.isdigit()]
            #got that from the internet, did not understand it but it works
            #http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return res

class Turnier():

    def _make_schedule(self):
        starthour = (self.start_time / 100)
        startminute = self.start_time % 100
        totaltime = 60*(24-starthour)-startminute
        self.timeframe = int(totaltime / self.g)
        self.schedule = [self.start_time]
        for i in range(1, self.g):
            last = self.schedule[-1]
            lasthour = (last / 100) * 100
            lastminute = last % 100
            minute = lastminute + self.timeframe
            hour = lasthour
            if minute > 59:
                minute -= 60
                hour += 100
            self.schedule.append(minute+hour)

    def __init__(self, filename=None, courts=3, start_time=2100, matchmaking=True, display_mmr=False, orgatime=3):
        if filename is None:
            filename = FILENAME
        with open(filename) as f:
            filecontent = f.readlines()
        names = []
        init_mmr = []
        self.max_name_len = 0
        for st in filecontent:
            spl = st.split()
            names.append(spl[0])
            if len(spl[0]) > self.max_name_len:
                max_name_len = len(spl[0])
            init_mmr.append(int(spl[1]))
        self.names = np.array(names)
        mmrlist = np.array(init_mmr)[:,None]
        self.matchmaking = matchmaking   #whether to sort teams before making matches (True) or to randomize (False)
        self.display_mmr = display_mmr   #whether to show mmr when announcing games
        self.orgatime = orgatime
        self.p = len(self.names)
        prange = [[el] for el in range(self.p)]
        pointlist = [[0]]*self.p
        pauselist = pointlist
        self.players = np.concatenate((prange,pointlist,pointlist,pointlist,pointlist,mmrlist,pauselist), axis=1)
        self.c = courts
        self.a = self.c*4
        self.w = self.p-self.a
        while self.w<0:
            self.c -= 1
            self.a = self.c*4
            self.w = self.p-self.a
            print("Anzahl der Felder korrigiert auf {}.".format(self.c))
        goodlist, waitlist, playlist = calc_game_count(self.p,self.w)
        print("{} Spieler registriert.".format(self.p))
        print("Mögliche Anzahl an Spielen:")
        print("Regulär: {} , Rize wartet eins mehr: {} , Rize spielt eins mehr: {}".format(goodlist, waitlist, playlist))
        self.g = int(raw_input("Wie viele Spiele sollen gespielt werden?\n"))   #python2.7
        self.rizemode = 0
        if self.g in waitlist:
            self.rizemode = -1
        elif self.g in playlist:
            self.rizemode = 1
        self.players[0,WAI] = self.rizemode
        self.maxwait = (self.g * self.w + self.rizemode) / self.p
        print("Anzahl der Spiele auf {} gesetzt. Rizemode auf {} gesetzt.".format(self.g,self.rizemode))
        self.start_time = start_time
        self._make_schedule()
        print("Zeit für jedes Spiel: {} Minuten + {} Minuten Organisation.".format(self.timeframe-self.orgatime, self.orgatime))
        self.i = 0     #number of games played so far
        print("Spielplan:")
        for i, t in enumerate(self.schedule):
            print("Spiel {}: {:02d}:{:02d} Uhr".format(i+1, t/100, t%100))
        self.games = []
        self.games_names = []
        self.results = []
        self.results = [[[]]*self.c]*self.g

    def game(self, wait_request=None):

        if wait_request is None:
            waitreq = []
        else:
            waitreq = list(wait_request)
        if (not [] == waitreq) and (1 == len(waitreq[0])):   #if it is just a string and not a list of strings
            waitreq = [waitreq]
        reqlist = []
        for reqname in waitreq:
            for ip, plname in enumerate(self.names):
                if plname.lower().startswith(reqname.lower()):
                    reqlist.append(ip)
                    break
        waiting_this_turn = np.array(reqlist).astype(int)
        wr = len(waiting_this_turn)
        if wr > self.w:
            waiting_this_turn = waiting_this_turn[:self.w]
        noreq = np.setdiff1d(self.players[:, IND], waiting_this_turn)
        wdif = self.w - wr
        for ip in waiting_this_turn:
            if self.players[ip, WAI] == self.maxwait:
                raise Exception("Player {} cannot wait anymore".format(self.names[ip]))

        print("Erstelle Spiel Nummer {}.".format(self.i+1))
        hour = self.schedule[self.i]/100
        minute = self.schedule[self.i]%100
        minute += self.timeframe - self.orgatime
        while minute > 60:
            hour += 1
            minute -= 60
        print("Planmäßig {:02d}:{:02d} - {:02d}:{:02d} Uhr".format(self.schedule[self.i]/100, self.schedule[self.i]%100, hour, minute))
        self.i += 1  # increment game counter
        if self.i == self.g:
            print("Dies ist das letzte Spiel!")
        min_wait = np.min(self.players[noreq,WAI])
        min_indices = np.intersect1d(np.where(min_wait == self.players[:,WAI])[0],noreq)
        if not len(min_indices) < wdif:
            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(min_indices, wdif, replace=False)))
        else:
            waiting_this_turn = np.concatenate((waiting_this_turn, min_indices))
            other_indices = np.setdiff1d(self.players[noreq, IND], min_indices)
            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(other_indices, wdif-len(min_indices), replace=False)))
        self.players[waiting_this_turn, WAI] += 1

        playing_this_turn = np.setdiff1d(self.players[:,IND], waiting_this_turn)    #all that are not waiting
        np.random.shuffle(playing_this_turn)                                        #shuffle them
        team_indices = np.array([[a, b] for a, b in zip(playing_this_turn[::2], playing_this_turn[1::2])])     #make teams of consecutive players in shuffled list
        teams = self.players[team_indices]

        if self.matchmaking:
            mmr = np.mean(teams[:,:,MMR].astype(float),axis=1)    #calculate match-making-ratio for each team
            mmr_sorted_indices = np.argsort(mmr)[::-1]   #no randomization of same mrr teams needed because players were already shuffled
            teams_sorted = teams[mmr_sorted_indices]     #now we have an array of teams that are descendingly sorted by mmr (strongest come first).
        else:
            teams_sorted = teams
        names_sorted = self.names[teams_sorted[:, :, IND]]
        self.games.append(teams_sorted)
        self.games_names.append(names_sorted)

        print("")
        for i in range(0,len(names_sorted),2):
            if self.display_mmr and self.matchmaking:
                sorted_mmr = mmr[mmr_sorted_indices]
                mmr1 = "{:2.1f}".format(sorted_mmr[i])
                mmr2 = "{:2.1f}".format(sorted_mmr[i+1])
                print("Feld {}: {:>7} / {:<7} {:>4} - {:<4} {:>7} / {:<7}".format([2, 1, 3][i / 2], names_sorted[i, 0],
                                                                                  names_sorted[i, 1], "(" + mmr1 + ")",
                                                                                  "(" + mmr2 + ")",
                                                                                  names_sorted[i + 1, 0],
                                                                                  names_sorted[i + 1, 1]))
            else:
                print("Feld {}: {:>7} / {:<7} - {:>7} / {:<7}".format([2,1,3][i/2],names_sorted[i,0], names_sorted[i,1], names_sorted[i+1,0], names_sorted[i+1,1]))
        print("")

        self.res()
        if self.i == self.g:
            print("")
            print("============ENDERGEBNIS=============")
            if self.rizemode == 0:
                self.stats(rize=True)
            else:
                self.stats(rize=False)

    def res(self, game_number=-1):
        self.players_copy = np.copy(self.players)
        if game_number == -1:
            game_number = self.i-1
        teams_sorted = self.games[game_number]
        names_sorted = self.games_names[game_number]
        entered = 0
        self.results[game_number] = [[]]*self.c
        while entered < len(names_sorted)/2:
            for ci in range(len(names_sorted)/2):  #ci = court index
                if not [] == self.results[game_number][ci]:   #was already entered
                    continue
                result_string = raw_input(
                    "Ergebnis für Spiel {:>7} / {:<7} - {:>7} / {:<7}: ".format(names_sorted[2*ci, 0],
                                                                                names_sorted[2*ci, 1],
                                                                                names_sorted[2*ci + 1, 0],
                                                                                names_sorted[2*ci + 1, 1]))  # python2.7
                res_numbers = split_result(result_string)
                cnt = len(res_numbers)
                if (not 0 == cnt) and (2*(cnt/2) == cnt): #if cnt > 0 and even number
                    self.results[game_number][ci] = [[]]*(cnt/2)     #in list for court make one list for each set played
                    for si in range(cnt/2):   #si = set index
                        score1 = res_numbers[2*si]
                        score2 = res_numbers[2*si+1]
                        scorediff = score1-score2
                        self.results[game_number][ci][si] = [score1, score2]

                        self.players[teams_sorted[2 * ci,0,IND], WON] += (np.sign(scorediff) + 1)
                        self.players[teams_sorted[2 * ci,1,IND], WON] += (np.sign(scorediff) + 1)
                        self.players[teams_sorted[2 * ci + 1,0,IND], WON] += (np.sign(-scorediff) + 1)
                        self.players[teams_sorted[2 * ci + 1,1,IND], WON] += (np.sign(-scorediff) + 1)

                        self.players[teams_sorted[2 * ci,0,IND], DIF] += scorediff
                        self.players[teams_sorted[2 * ci, 1, IND], DIF] += scorediff
                        self.players[teams_sorted[2 * ci+1, 0, IND], DIF] -= scorediff
                        self.players[teams_sorted[2 * ci+1, 1, IND], DIF] -= scorediff

                        self.players[teams_sorted[2 * ci, 0, IND], POI] += score1
                        self.players[teams_sorted[2 * ci, 1, IND], POI] += score1
                        self.players[teams_sorted[2 * ci + 1, 0, IND], POI_OPP] += score1
                        self.players[teams_sorted[2 * ci + 1, 1, IND], POI_OPP] += score1

                        self.players[teams_sorted[2 * ci, 0, IND], POI_OPP] += score2
                        self.players[teams_sorted[2 * ci, 1, IND], POI_OPP] += score2
                        self.players[teams_sorted[2 * ci + 1, 0, IND], POI] += score2
                        self.players[teams_sorted[2 * ci + 1, 1, IND], POI] += score2

                        self.players[teams_sorted[2 * ci, 0, IND], MMR] += np.sign(scorediff)
                        self.players[teams_sorted[2 * ci, 1, IND], MMR] += np.sign(scorediff)
                        self.players[teams_sorted[2 * ci + 1, 0, IND], MMR] += np.sign(-scorediff)
                        self.players[teams_sorted[2 * ci + 1, 1, IND], MMR] += np.sign(-scorediff)
                    entered += 1

    def stats(self, rize=True):
        print("")
        sort_indices = np.lexsort((self.players[:,POI_OPP], -self.players[:,POI], -self.players[:,DIF], -self.players[:,WON]))
        stats_sorted = self.players[sort_indices]
        names_sorted = self.names[sort_indices]
        print("{:<8} {:<8} {:<8} {:<8} {:<8}".format("Spieler", "Sätze", "Diff", "Punkte", "Gegn. P."))
        print("")
        for pi, name in enumerate(names_sorted):
            if (not rize) and (name.lower().startswith("rize")):
                continue
            print("{:<8} {:<8} {:<8} {:<8} {:<8}".format(name, stats_sorted[pi, WON]/2, stats_sorted[pi, DIF], stats_sorted[pi, POI], stats_sorted[pi, POI_OPP]))
        print("")

    def cor_res(self):
        self.players = np.copy(self.players_copy)
        self.res()