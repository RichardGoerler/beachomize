# -*- coding: utf-8 -*-

import numpy as np

import pickle

MMR_NONE = 0
MMR_FLAT = 1
MMR_FLAT_STREAK = 2
MMR_DIFF = 3
MMR_DIFF_STREAK = 4
MMR_METHODS = ["none", "flat", "flat streak", "diff", "diff streak"]
MMR_TAG_CUM = 0
MMR_TAG_IND = 1
MMR_TAGS = ["cumulative", "individual"]

def load(gui, filename="saved.p"):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    obj.gui = gui
    return obj


def lcm1(f):
    ff = f
    while not ff == int(ff):
        ff += f
    return int(ff)


class Turnier:

    def _make_schedule(self):
        durhour = int(self.duration / 100)
        durminute = self.duration % 100
        totaltime = 60*durhour + durminute
        self.timeframe = int(totaltime / self.g)
        self.schedule = [self.start_time]
        for i in range(1, self.g):
            last = self.schedule[-1]
            lasthour = int(last / 100) * 100
            lastminute = last % 100
            minute = lastminute + self.timeframe
            hour = lasthour
            if minute > 59:
                minute -= 60
                hour += 100
            hour %= 2400
            self.schedule.append(minute+hour)

    def calc_game_counts(self):
        f = self.w  # player position in round waiting queue
        i = 1  # number of games played
        r = 2  # number of waiting rounds to test (when 1, calculation is aborted the first time f is zero)
        while not r == 0:
            if self.p == f + 1:  # if one player (player 0) can play a game more to make it work
                self.playlist.append(i)
            if f == 1:  # if one player (player 0) can wait a game more
                self.waitlist.append(i)
            if f == 0:  # if it works regularly
                self.goodlist.append(i)
                r -= 1
            f += self.w
            f %= self.p
            i += 1

    def games_intervalwise(self, games):
        PRECISION = 2
        if self.t2 == 1.:
            return [0,games,0]
        step = 1./games
        progress = 0.
        interval = 1
        int_list = [0, self.t1, self.t2, self.t3]
        out_long = self.c13 < self.c2     #bool, true if outer interval games overlap into the inner interval, false if the other way round
        g = [0,0,0]
        while not round(progress+step, PRECISION) > 1.:
            out = (interval-1)%2 == 0           #bool, True if in t1 or t3, False if in t2
            offset = sum(int_list[0:interval])
            int_progress = progress - offset
            progress += step
            int_remainder = int_list[interval] - int_progress
            if round(int_remainder, PRECISION) > round(step, PRECISION):     #if step fits into interval remainder
                g[interval - 1] += 1                            #then just add the game to the interval
            elif out_long == out or round(int_remainder, PRECISION) == round(step, PRECISION):  #if the game would overlap into (and that is allowed by out_long) or fit exactly into the next interval
                g[interval - 1] += 1                            #then add the game to the interval and switch to the next interval
                interval += 1
                if round(int_list[interval], PRECISION) < round(step, PRECISION):  #but if this interval is too short to fit an entire game, switch to the next after that
                    interval += 1
            else:                                          #if the current interval is not able to overlap (but the next)
                interval += 1                                   #switch to the next interval and add the game to that one
                g[interval - 1] += 1
                offset = sum(int_list[0:interval])
                int_progress = progress - offset
                if int_list[interval] - int_progress < 0 + PRECISION:       #if the next interval was so short, that we already completely used it
                    interval += 1                                   #switch to the next after that.
        return g


    def calc_game_counts2(self, max_g = 20):
        self.maxwait_list = [0]*max_g
        wait_list = [self.w13, self.w2, self.w13]
        for gi in range(1, max_g):                         #gi: game count to test
            g_ints = self.games_intervalwise(gi)
            f = 0                                       #f: player position in round waiting queue
            wraps = 0
            for interval_index in range(3):                 #the three intervals are gone through one after another
                for _ in range(g_ints[interval_index]):         #iterate through the games that are played in that interval
                    f += wait_list[interval_index]
                    if not f < self.p:                      #not using modulus here because we want to get the number of times we wrapped around. This is in the end the number of appearances of each player.
                        f -= self.p
                        wraps += 1
            if self.p == f + 1:  # if one player (player 0) can play a game more to make it work
                self.playlist.append(gi)
            elif f == 1:  # if one player (player 0) can wait a game more
                self.waitlist.append(gi)
            elif f == 0:  # if it works regularly
                self.goodlist.append(gi)
            self.maxwait_list[gi] = wraps



    def __init__(self, names, mmr, courts=3, courts13=3, start_time=2100, duration=300, t1=0., t2=1., t3=0., matchmaking=MMR_DIFF_STREAK, matchmaking_tag=MMR_TAG_CUM, display_mmr=False, orgatime=3):
        self.init_mmr = mmr
        self.start_time = start_time
        self.duration = duration
        #consists of three intervals t1..t2..t3 at max. These numbers are proportions of the total time. t1 and t3 take place the same number of courts.
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.p = len(names)
        dt = np.dtype([('index', int), ('name', object), ('score', int), ('diff', int), ('points', int), ('mmr', float), ('wait', int), ('mmr_tag_w', int), ('mmr_tag_l', int)])
        self.players = np.recarray(self.p, dtype=dt)
        self.players["index"] = np.arange(self.p)
        self.players["name"] = names
        self.players["mmr"] = self.init_mmr
        self.players["score"] = self.players["diff"] = self.players["points"] = self.players["wait"] = self.players["mmr_tag_w"] = self.players["mmr_tag_l"] = [0]*self.p
        self.players_copy = None
        self.partner_matrix = np.zeros((self.p, self.p))
        self.matchmaking = matchmaking   # whether to sort teams before making matches (True) or to randomize (False). If True, different methods apply (see constants)
        self.matchmaking_tag = matchmaking_tag   #whether to update mmr tag (streak information) after each set or after each game with cumulative score-difference
        self.display_mmr = display_mmr   # whether to show mmr when announcing games
        self.orgatime = orgatime
        self.c2 = courts    #courts during middle interval
        self.c13 = courts13   #courts during outer intervals
        self.a2 = self.c2*4
        self.a13 = self.c13 * 4
        self.w2 = self.p-self.a2
        self.w13 = self.p - self.a13
        while self.w2 < 0:
            self.c2 -= 1
            self.a2 = self.c2*4
            self.w2 = self.p-self.a2
        while self.w13 < 0:
            self.c13 -= 1
            self.a13 = self.c13*4
            self.w13 = self.p-self.a13
        if self.t2 == 0:
            self.c2 = self.c13
        if self.c2 == self.c13:
            self.t1 = self.t3 = 0.
            self.t2 = 1.
        self.rizemode = 0
        self.i = 0  # number of games played so far
        self.state = -1  # -1: just initialized 0: after setting game count 1: after game announcement, 2: after entering results, 3: after correcting results
        self.games = []
        self.games_names = []
        self.results = []
        self.waitlist = []
        self.playlist = []
        self.goodlist = []
        self.calc_game_counts2()
        self.g = 0

    def set_game_count(self, g):
        self.g = g
        if self.g in self.waitlist:
            self.rizemode = -1
        elif self.g in self.playlist:
            self.rizemode = 1
        self.players[0].wait = self.rizemode
        self.maxwait = self.maxwait_list[self.g]
        self.appearances = self.g - self.maxwait
        self.g_list = self.games_intervalwise(self.g)
        if self.g_list[0] == 0:
            self.interval = 2     #interval saves which interval turnier is currently in. beginning with 1, not with zero because of alignment with variable names and other reasons
            self.w = self.w2
            self.c = self.c2
        else:
            self.interval = 1
            self.w = self.w13
            self.c = self.c13
        self._make_schedule()
        self.results = [[[]]*self.c13]*self.g_list[0]
        self.results.extend([[[]]*self.c2]*self.g_list[1])
        self.results.extend([[[]] * self.c13] * self.g_list[2])
        self.state = 0
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

    def canwait(self, waitlist, return_changed = False):
        changed = False
        if waitlist is None:
            return np.array([])
        waiting_this_turn = []
        wr = len(waitlist)
        if wr > self.w:
            wr = self.w
            changed = True
        for i in range(wr):
            if self.players[waitlist[i]].wait < self.maxwait:
                waiting_this_turn.append(waitlist[i])
            else:
                changed = True
        ret = np.array(waiting_this_turn).astype(int)
        if return_changed:
            return changed, ret
        return ret

    def game(self, wait_request=None):
        if self.g < 1:
            return -1
        if self.interval == 1:
            if self.i == self.g_list[0]:
                self.interval = 2
                self.w = self.w2
                self.c = self.c2
        if self.interval == 2:
            if self.i == self.g_list[1]+self.g_list[0]:
                self.interval = 3
                self.w = self.w13
                self.c = self.c13
        ret = 0    #0 no matrix reset, 1 regular matrix reset, 2 error matrix reset
        #WAITING
        waiting_this_turn = self.canwait(wait_request)
        wr = len(waiting_this_turn)
        noreq = np.setdiff1d(self.players.index, waiting_this_turn)
        wdif = self.w - wr
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
            self.partner_matrix = np.zeros((self.p, self.p))
            ret = 1
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
                    self.partner_matrix = np.zeros((self.p, self.p))
                    ret = 2
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
            temp_mmr = np.mean(teams.mmr.astype(float), axis=1)    # calculate match-making-ratio for each team
            temp_mmr_sorted_indices = np.argsort(temp_mmr)[::-1]
            teams_sorted = teams[temp_mmr_sorted_indices]     # descendingly sorted by mmr (strongest come first).
        else:
            teams_sorted = teams
        self.games.append(teams_sorted.index)

        self.state = 1
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

        return ret

    # def game_announce_end(self, message_prefix=""):
    #     if self.display_mmr and self.matchmaking:
    #         sorted_mmr = self.temp_mmr[self.temp_mmr_sorted_indices]
    #         nogui.out_game_announce_teams(self.temp_players_sorted, sorted_mmr)
    #     else:
    #         nogui.out_game_announce_teams(self.temp_players_sorted)

        # EXPECTING RESULTS
        # self.res()
        # if self.i == self.g:
        #     if self.rizemode == 0:
        #         self.stats(rize=True, final=True)
        #     else:
        #         self.stats(rize=False, final=True)

    def res(self, res, game_number=-1):
        self.players_copy = self.players.copy()
        if game_number == -1:
            game_number = self.i-1
        team_indices_sorted = self.games[game_number]
        self.results[game_number] = res
        for ci, court_results in enumerate(self.results[game_number]):  # ci = court index
            cumdiff = 0
            for set_result in court_results:   # si = set index
                pl = self.players[team_indices_sorted[2 * ci:2 * ci + 2]]  # I know the values are copied here, but I buy myself readability in mmr lines by keeping them short and pay with efficiency
                score1 = set_result[0]
                score2 = set_result[1]
                scorediff = score1-score2
                cumdiff += scorediff

                # generate index 0: lost, 1: draw, 2: won. index default score array with that index
                self.players[team_indices_sorted[2 * ci, 0]].score += [0, 0, 1][np.sign(scorediff) + 1]
                self.players[team_indices_sorted[2 * ci, 1]].score += [0, 0, 1][np.sign(scorediff) + 1]
                self.players[team_indices_sorted[2 * ci + 1, 0]].score += [0, 0, 1][np.sign(-scorediff) + 1]
                self.players[team_indices_sorted[2 * ci + 1, 1]].score += [0, 0, 1][np.sign(-scorediff) + 1]

                # difference is from the POV of team 1, so positive if team 1 won
                self.players[team_indices_sorted[2 * ci, 0]].diff += scorediff
                self.players[team_indices_sorted[2 * ci, 1]].diff += scorediff
                self.players[team_indices_sorted[2 * ci + 1, 0]].diff -= scorediff
                self.players[team_indices_sorted[2 * ci + 1, 1]].diff -= scorediff

                self.players[team_indices_sorted[2 * ci, 0]].points += score1
                self.players[team_indices_sorted[2 * ci, 1]].points += score1
                self.players[team_indices_sorted[2 * ci + 1, 0]].points += score2
                self.players[team_indices_sorted[2 * ci + 1, 1]].points += score2

                if self.matchmaking == MMR_DIFF_STREAK:
                    # according to mmr_tags scorediff is multiplied with 0.3, 0.6 or 1. When on winning/losing streak, game outcomes are more strongly weighted
                    # this is intended to decrease the influence of random fluctuations in performance
                    self.players[team_indices_sorted[2 * ci, 0]].mmr += scorediff*[0.3, 0.6, 1][pl[0,0].mmr_tag_w] if scorediff > 0 else scorediff*[0.3, 0.6, 1][pl[0,0].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci, 1]].mmr += scorediff*[0.3, 0.6, 1][pl[0,1].mmr_tag_w] if scorediff > 0 else scorediff*[0.3, 0.6, 1][pl[0,1].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci + 1, 0]].mmr -= scorediff*[0.3, 0.6, 1][pl[1,0].mmr_tag_w] if scorediff < 0 else scorediff*[0.3, 0.6, 1][pl[1,0].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci + 1, 1]].mmr -= scorediff*[0.3, 0.6, 1][pl[1,1].mmr_tag_w] if scorediff < 0 else scorediff*[0.3, 0.6, 1][pl[1,1].mmr_tag_l]

                if self.matchmaking == MMR_FLAT_STREAK:
                    #same as diff streak, but is multiplied with one, irrespective of points dfference
                    self.players[team_indices_sorted[2 * ci, 0]].mmr += [0.3, 0.6, 1][pl[0, 0].mmr_tag_w] if scorediff > 0 else [-0.3, -0.6, -1][pl[0, 0].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci, 1]].mmr += [0.3, 0.6, 1][pl[0, 1].mmr_tag_w] if scorediff > 0 else [-0.3, -0.6, -1][pl[0, 1].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci + 1, 0]].mmr -= [0.3, 0.6, 1][pl[1, 0].mmr_tag_w] if scorediff < 0 else [-0.3, -0.6, -1][pl[1, 0].mmr_tag_l]
                    self.players[team_indices_sorted[2 * ci + 1, 1]].mmr -= [0.3, 0.6, 1][pl[1, 1].mmr_tag_w] if scorediff < 0 else [-0.3, -0.6, -1][pl[1, 1].mmr_tag_l]

                if self.matchmaking == MMR_DIFF:
                    #mmr is the same as points difference
                    self.players[team_indices_sorted[2 * ci, 0]].mmr += scorediff
                    self.players[team_indices_sorted[2 * ci, 1]].mmr += scorediff
                    self.players[team_indices_sorted[2 * ci + 1, 0]].mmr -= scorediff
                    self.players[team_indices_sorted[2 * ci + 1, 1]].mmr -= scorediff

                if self.matchmaking == MMR_FLAT:
                    # generate index 0: lost, 1: draw, 2: won. index mmr array with that in a way that lose means -1, draw means 0 and win means +1
                    self.players[team_indices_sorted[2 * ci, 0]].mmr += [-1, 0, 1][np.sign(scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci, 1]].mmr += [-1, 0, 1][np.sign(scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci + 1, 0]].mmr += [-1, 0, 1][np.sign(-scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci + 1, 1]].mmr += [-1, 0, 1][np.sign(-scorediff) + 1]

                if self.matchmaking_tag == MMR_TAG_IND:
                    self._update_mmr_tag(ci, team_indices_sorted, scorediff)

            if self.matchmaking_tag == MMR_TAG_CUM:
                self._update_mmr_tag(ci, team_indices_sorted, cumdiff)

        if self.state == 1:
            self.state = 2
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

    def _update_mmr_tag(self, ci, teams, diff):
        # mmr_tag_w keeps track of number of wins {0,1,2} and mmr_tag_l accordingly for losses
        # mmr_tag_w is increased in case of win, mmr_tag_l is decreased and vice versa. In case of tie both are decreased
        self.players[teams[2 * ci, 0]].mmr_tag_w += 1 if diff > 0 else -1
        self.players[teams[2 * ci, 1]].mmr_tag_w += 1 if diff > 0 else -1
        self.players[teams[2 * ci + 1, 0]].mmr_tag_w += 1 if diff < 0 else -1
        self.players[teams[2 * ci + 1, 1]].mmr_tag_w += 1 if diff < 0 else -1

        self.players[teams[2 * ci, 0]].mmr_tag_l += 1 if diff < 0 else -1
        self.players[teams[2 * ci, 1]].mmr_tag_l += 1 if diff < 0 else -1
        self.players[teams[2 * ci + 1, 0]].mmr_tag_l += 1 if diff > 0 else -1
        self.players[teams[2 * ci + 1, 1]].mmr_tag_l += 1 if diff > 0 else -1

        for ti in range(0, 2):
            for pi in range(0, 2):
                self.players[teams[2 * ci + ti, pi]].mmr_tag_w = min(max(self.players[teams[2 * ci + ti, pi]].mmr_tag_w, 0), 2)
                self.players[teams[2 * ci + ti, pi]].mmr_tag_l = min(max(self.players[teams[2 * ci + ti, pi]].mmr_tag_l, 0), 2)

    def cor_res(self, res):
        self.state = 3
        self.players = self.players_copy.copy()
        self.res(res)

    # def stats(self, rize=True, final=False):
    #     nogui.out_stats(self.players, rize, final)

    # def continue_after_load(self):
    #     if self.state == 1:
    #         self.game_announce_end()

    def __getstate__(self):
        return dict((k, v) for (k, v) in self.__dict__.items() if "gui" not in k)
