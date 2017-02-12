# -*- coding: utf-8 -*-

import nogui

import numpy as np

import pickle


def load(gui, filename="saved.p"):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    obj.gui = gui
    return obj


def calc_game_count(p, w):
    waitlist = []
    playlist = []
    goodlist = []
    f = w    # player position in round waiting queue
    i = 1    # number of games played
    r = 2    # number of waiting rounds to test (when 1, calculation is aborted the first time f is zero)
    while not r == 0:
        if p == f+1:    # if one player (Rize) can play a game more to make it work
            playlist.append(i)
        if f == 1:      # if one player (Rize) can wait a game more
            waitlist.append(i)
        if f == 0:      # if it works regularly
            goodlist.append(i)
            r -= 1
        f += w
        f %= p
        i += 1
    return goodlist, waitlist, playlist


def lcm1(f):
    ff = f
    while not ff == int(ff):
        ff += f
    return int(ff)


class Turnier:

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

    def __init__(self, gui, courts=3, start_time=2100, matchmaking=True, display_mmr=False, orgatime=3):
        self.gui = gui
        names, self.init_mmr = nogui.in_players()
        self.p = len(names)
        dt = np.dtype([('index', int), ('name', object), ('score', int), ('diff', int), ('points', int), ('mmr', float),
                       ('wait', int)])
        self.players = np.recarray(self.p, dtype=dt)
        self.players.index = np.arange(self.p)
        self.players.name = names
        self.players.mmr = self.init_mmr
        self.players.score = self.players.diff = self.players.points = self.players.wait = [0]*self.p
        self.players_copy = None
        self.partner_matrix = np.zeros((self.p, self.p))
        self.matchmaking = matchmaking   # whether to sort teams before making matches (True) or to randomize (False)
        self.display_mmr = display_mmr   # whether to show mmr when announcing games
        self.orgatime = orgatime
        self.c = courts
        self.a = self.c*4
        self.w = self.p-self.a
        while self.w < 0:
            self.c -= 1
            self.a = self.c*4
            self.w = self.p-self.a
            nogui.out_court_number_changed(self.c)
        goodlist, waitlist, playlist = calc_game_count(self.p, self.w)
        self.gui.out_player_count(self.p)
        self.g = nogui.in_game_count(goodlist, waitlist, playlist)
        self.rizemode = 0
        if self.g in waitlist:
            self.rizemode = -1
        elif self.g in playlist:
            self.rizemode = 1
        self.players[0].wait = self.rizemode
        self.maxwait = (self.g * self.w + self.rizemode) / self.p
        nogui.out_game_count(self.g, self.rizemode)
        self.start_time = start_time
        self._make_schedule()
        self.i = 0  # number of games played so far
        nogui.out_schedule(self.timeframe, self.orgatime, self.schedule)
        self.games = []
        self.games_names = []
        self.results = []
        self.results = [[[]]*self.c]*self.g

        self.state = 0     # 0: after init or after entering results 2: expect results
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)


    def game(self, wait_request=None):
        # WAITING
        if wait_request is None:
            waitreq = []
        else:
            waitreq = list(wait_request)
        if (not [] == waitreq) and (1 == len(waitreq[0])):   # if it is just a string and not a list of strings
            waitreq = [waitreq]
        reqlist = []
        for reqname in waitreq:
            for ip, plname in enumerate(self.players.name):
                if plname.lower().startswith(reqname.lower()):
                    reqlist.append(ip)
                    break
        waiting_this_turn = np.array(reqlist).astype(int)
        wr = len(waiting_this_turn)
        if wr > self.w:
            waiting_this_turn = waiting_this_turn[:self.w]
        noreq = np.setdiff1d(self.players.index, waiting_this_turn)
        wdif = self.w - wr
        for ip in waiting_this_turn:
            if self.players[ip].wait == self.maxwait:
                raise Exception("Player {} cannot wait anymore".format(self.players[ip].name))
        nogui.out_game_announce_time(self.timeframe, self.orgatime, self.schedule, self.g, self.i)
        self.i += 1  # increment game counter
        min_wait = np.min(self.players.wait[noreq])
        min_indices = np.intersect1d(np.where(min_wait == self.players.wait)[0], noreq)
        if not len(min_indices) < wdif:
            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(min_indices, wdif, replace=False)))
        else:
            waiting_this_turn = np.concatenate((waiting_this_turn, min_indices))
            other_indices = np.setdiff1d(self.players.index[noreq], min_indices)
            waiting_this_turn = np.concatenate(
                (waiting_this_turn, np.random.choice(other_indices, wdif - len(min_indices), replace=False)))
        self.players.wait[waiting_this_turn] += 1

        # MAKING TEAMS (OLD METHOD)
        # playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)    # all that are not waiting
        # np.random.shuffle(playing_this_turn)                                        # shuffle them
        # # make teams of consecutive players in shuffled list
        # team_indices = np.array([[a, b] for a, b in zip(playing_this_turn[::2], playing_this_turn[1::2])])
        # teams = self.players[team_indices]

        # MAKING TEAMS (NEW METHOD)
        if 0 == len(np.where(self.partner_matrix == 0)[0]):  # if partner matrix all 1, reset it
            nogui.out_reset_partner_matrix()
            self.partner_matrix = np.zeros((self.p, self.p))
        teams_ready = False
        while not teams_ready:
            playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)  # all that are not waiting
            playing_partner_matrix = self.partner_matrix[playing_this_turn][:, playing_this_turn]
            team_indices = []
            for ti in range(2*self.c):  # ti = team index
                counts = np.array([len(row)-np.count_nonzero(row) for row in playing_partner_matrix])
                lexsort_ind = np.lexsort((np.random.rand(len(counts)), counts))
                # choose player with fewest matching possibilities
                pid = lexsort_ind[0]
                pl = playing_this_turn[pid]
                # delete pl's column from temp matrix and delete pl from playing_this_turn
                playing_partner_matrix = np.delete(playing_partner_matrix, pid, axis=1)
                playing_this_turn = np.delete(playing_this_turn, pid)
                # get player's row from matrix
                player_row = playing_partner_matrix[pid, :]
                # get indices of still zero entries and select one at random
                zero_entries_indices = np.where(player_row == 0)[0]
                if 0 == len(zero_entries_indices):  # if no choice possible, reset partner matrix & restart team making
                    nogui.out_reset_partner_matrix_error()
                    self.partner_matrix = np.zeros((self.p, self.p))
                    break
                choice = np.random.choice(zero_entries_indices)
                # get partner for pl
                par = playing_this_turn[choice]
                # set corresponding indices in partner_matrix to 1
                self.partner_matrix[pl, par] = 1
                self.partner_matrix[par, pl] = 1
                # now delete also pl's row from temp matrix
                playing_partner_matrix = np.delete(playing_partner_matrix, pid, axis=0)
                # and delete par's row and column and delete par from playing_this_turn
                playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=0)
                playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=1)
                playing_this_turn = np.delete(playing_this_turn, choice)
                # add team to teams list
                team_indices.append([pl, par])
            teams_ready = True
        team_indices = np.array(team_indices)
        teams = self.players[team_indices]

        # MATCHMAKING
        if self.matchmaking:
            self.temp_mmr = np.mean(teams[:, :].mmr.astype(float), axis=1)    # calculate match-making-ratio for each team
            self.temp_mmr_sorted_indices = np.argsort(self.temp_mmr)[::-1]
            team_indices_sorted = teams[self.temp_mmr_sorted_indices]     # descendingly sorted by mmr (strongest come first).
        else:
            team_indices_sorted = teams
        self.temp_players_sorted = self.players[team_indices_sorted.index]
        self.games.append(team_indices_sorted.index)

        self.state = 1
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

        self.game_announce_end()

    def game_announce_end(self):
        if self.display_mmr and self.matchmaking:
            sorted_mmr = self.temp_mmr[self.temp_mmr_sorted_indices]
            nogui.out_game_announce_teams(self.temp_players_sorted, sorted_mmr)
        else:
            nogui.out_game_announce_teams(self.temp_players_sorted)

        # EXPECTING RESULTS
        self.res()
        if self.i == self.g:
            if self.rizemode == 0:
                self.stats(rize=True, final=True)
            else:
                self.stats(rize=False, final=True)

    def res(self, game_number=-1):
        self.players_copy = np.copy(self.players)
        if game_number == -1:
            game_number = self.i-1
        team_indices_sorted = self.games[game_number]
        players_sorted = self.players[team_indices_sorted]
        self.results[game_number] = nogui.in_results(self.c, players_sorted)
        for ci, court_results in enumerate(self.results[game_number]):  # ci = court index
                for set_result in court_results:   # si = set index
                    score1 = set_result[0]
                    score2 = set_result[1]
                    scorediff = score1-score2

                    # generate index 0: lost, 1: draw, 2: won. index default score array with that index
                    self.players[team_indices_sorted[2 * ci, 0]].score += [0, 0, 1][np.sign(scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci, 1]].score += [0, 0, 1][np.sign(scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci + 1, 0]].score += [0, 0, 1][np.sign(-scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci + 1, 1]].score += [0, 0, 1][np.sign(-scorediff) + 1]

                    # difference is from the POV of team 1, so positive if team 1 won
                    self.players[team_indices_sorted[2 * ci, 0]].diff += scorediff
                    self.players[team_indices_sorted[2 * ci, 1]].diff += scorediff
                    self.players[team_indices_sorted[2 * ci+1, 0]].diff -= scorediff
                    self.players[team_indices_sorted[2 * ci+1, 1]].diff -= scorediff

                    self.players[team_indices_sorted[2 * ci, 0]].points += score1
                    self.players[team_indices_sorted[2 * ci, 1]].points += score1
                    self.players[team_indices_sorted[2 * ci + 1, 0]].points += score2
                    self.players[team_indices_sorted[2 * ci + 1, 1]].points += score2

                    # mmr is changed according to score difference at the moment, may be changed later
                    # this means, when initialized with 0, mmr = diff at the end of the day
                    self.players[team_indices_sorted[2 * ci, 0]].mmr += scorediff
                    self.players[team_indices_sorted[2 * ci, 1]].mmr += scorediff
                    self.players[team_indices_sorted[2 * ci + 1, 0]].mmr -= scorediff
                    self.players[team_indices_sorted[2 * ci + 1, 1]].mmr -= scorediff

        self.state = 0
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

    def stats(self, rize=True, final=False):
        nogui.out_stats(self.players, rize, final)

    def cor_res(self):
        self.players = np.copy(self.players_copy)
        self.res()

    def continue_after_load(self):
        if self.state == 1:
            self.game_announce_end()
