# -*- coding: utf-8 -*-

import numpy as np

import pickle

import pdb

# matchmaking variable: List of booleans [consider score difference, consider mmr difference, consider win / loss streak (MMR tags)]
MMR_TAG_CUM = 0
MMR_TAG_IND = 1
MMR_TAGS = ["cumulative", "individual"]
TRIES = 100
PRED_CORR_DISCOUNT = 0.5
UNCONSTRAINED_GAME_NUMBER = 30

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
        PRECISION = 5
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
                if interval < 3 and round(int_list[interval], PRECISION) < round(step, PRECISION):  #but if this interval is too short to fit an entire game, switch to the next after that
                    interval += 1
            else:                                          #if the current interval is not able to overlap (but the next)
                interval += 1                                   #switch to the next interval and add the game to that one
                g[interval - 1] += 1
                offset = sum(int_list[0:interval])
                int_progress = progress - offset
                int_remainder = int_list[interval] - int_progress
                if round(int_remainder, PRECISION) < 0:       #if the next interval was so short, that we already completely used it
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
                self.maxwait_list[gi] = wraps+1
            elif f == 1:  # if one player (player 0) can wait a game more
                self.waitlist.append(gi)
                self.maxwait_list[gi] = wraps
            elif f == 0:  # if it works regularly
                self.goodlist.append(gi)
                self.maxwait_list[gi] = wraps
                good_found = True
            elif self.p == f + 2:  # player 0 can play 2 games more
                if wraps > 0:
                    appearances = gi - (wraps + 1)
                    if (appearances + 2) <= gi:         # in some cases, calculation may yield game number that is not possible because of excess player one games
                        self.playlist2.append(gi)
                        self.maxwait_list[gi] = wraps+1
            elif f == 2:
                appearances = gi - wraps
                if (appearances - 2) >= 0:             # in some cases, calculation may yield game number that is not possible because of negative player one games
                    self.waitlist2.append(gi)
                    self.maxwait_list[gi] = wraps
            elif self.p == f + 3:  # player 0 can play 3 games more
                if wraps > 0:
                    appearances = gi - (wraps + 1)
                    if (appearances + 3) <= gi:        # same as above
                        self.playlist3.append(gi)
                        self.maxwait_list[gi] = wraps+1
            elif f == 3:
                appearances = gi - wraps
                if (appearances - 3) >= 0:              # same
                    self.waitlist3.append(gi)
                    self.maxwait_list[gi] = wraps



    def cgc_complete(self, begin=4, end=41):
        self_cp = dict(self.__dict__)
        playl = []
        waitl = []
        goodl = []
        playl2 = []
        waitl2 = []
        playl3 = []
        waitl3 = []
        for ppp in range(begin,end):
            self.p = ppp
            self.waitlist = []
            self.playlist = []
            self.goodlist = []
            self.waitlist2 = []
            self.playlist2 = []
            self.waitlist3 = []
            self.playlist3 = []
            self.t1 = self.t1_init
            self.t2 = self.t2_init
            self.t3 = self.t3_init
            self.c2 = self.c2_init
            self.c13 = self.c13_init
            self.a2 = self.c2 * 2 * self.teamsize
            self.a13 = self.c13 * 2 * self.teamsize
            self.w2 = self.p - self.a2
            self.w13 = self.p - self.a13
            while self.w2 < 0:
                self.c2 -= 1
                self.a2 = self.c2 * 2 * self.teamsize
                self.w2 = self.p - self.a2
            while self.w13 < 0:
                self.c13 -= 1
                self.a13 = self.c13 * 2 * self.teamsize
                self.w13 = self.p - self.a13
            if self.t2 == 0:
                self.c2 = self.c13
            elif self.t1 == 0 and self.t3 == 0:
                self.c13 = self.c2
            if self.c2 == self.c13:
                self.t1 = self.t3 = 0.
                self.t2 = 1.
            self.calc_game_counts2()
            playl.append(self.playlist)
            waitl.append(self.waitlist)
            goodl.append(self.goodlist)
            playl2.append(self.playlist2)
            waitl2.append(self.waitlist2)
            playl3.append(self.playlist3)
            waitl3.append(self.waitlist3)
            print("")
            row_format = "{:>2} | good | " + "{:>2} " * len(self.goodlist)
            print(row_format.format(ppp, *self.goodlist))
            row_format = "{:>2} | wait | " + "{:>2} " * len(self.waitlist)
            print(row_format.format(ppp, *self.waitlist))
            row_format = "{:>2} | play | " + "{:>2} " * len(self.playlist)
            print(row_format.format(ppp, *self.playlist))
            row_format = "{:>2} | wai2 | " + "{:>2} " * len(self.waitlist2)
            print(row_format.format(ppp, *self.waitlist2))
            row_format = "{:>2} | pla2 | " + "{:>2} " * len(self.playlist2)
            print(row_format.format(ppp, *self.playlist2))
            row_format = "{:>2} | wai3 | " + "{:>2} " * len(self.waitlist3)
            print(row_format.format(ppp, *self.waitlist3))
            row_format = "{:>2} | pla3 | " + "{:>2} " * len(self.playlist3)
            print(row_format.format(ppp, *self.playlist3))
        self.p = self_cp['p']
        self.waitlist = self_cp['waitlist']
        self.playlist = self_cp['playlist']
        self.goodlist = self_cp['goodlist']
        self.waitlist2 = self_cp['waitlist2']
        self.playlist2 = self_cp['playlist2']
        self.waitlist3 = self_cp['waitlist3']
        self.playlist3 = self_cp['playlist3']
        self.t1 = self_cp['t1']
        self.t2 = self_cp['t2']
        self.t3 = self_cp['t3']
        self.c2 = self_cp['c2']
        self.c13 = self_cp['c13']


    def __init__(self, names, mmr, courts=3, courts13=3, start_time=2100, duration=300, t1=0., t2=1., t3=0., matchmaking=[1, 1, 1], matchmaking_tag=MMR_TAG_CUM, females=0, display_mmr=False, orgatime=3, teamsize=2):
        self.init_mmr = mmr
        self.start_time = start_time
        self.duration = duration
        self.females = females
        #consists of three intervals t1..t2..t3 at max. These numbers are proportions of the total time. t1 and t3 take place the same number of courts.
        self.t1 = self.t1_init = t1
        self.t2 = self.t2_init = t2
        self.t3 = self.t3_init = t3
        self.p = len(names)
        dt = np.dtype([('index', int), ('name', object), ('score', int), ('diff', int), ('points', int), ('mmr', float), ('wait', int), ('wait_prob', int), ('mmr_tag_w', int), ('mmr_tag_l', int)])
        self.players = np.recarray(self.p, dtype=dt)
        self.players["index"] = np.arange(self.p)
        self.players["name"] = names
        self.players["mmr"] = self.init_mmr
        self.players["score"] = self.players["diff"] = self.players["points"] = self.players["wait"] = self.players["mmr_tag_w"] = self.players["mmr_tag_l"] = [0]*self.p
        self.players["wait_prob"] = [2]*self.p
        self.players_copy = None
        self.female_ratio = self.females / self.p
        self.matchmaking = matchmaking   # List of booleans [consider score difference, consider mmr difference, consider win / loss streak (MMR tags)]
        self.matchmaking_tag = matchmaking_tag   #whether to update mmr tag (streak information) after each set or after each game with cumulative score-difference
        self.display_mmr = display_mmr   # whether to show mmr when announcing games
        self.orgatime = orgatime
        self.teamsize = teamsize
        self.c2 = self.c2_init = courts    #courts during middle interval
        self.c13 = self.c13_init = courts13   #courts during outer intervals
        self.a2 = self.c2*2*self.teamsize
        self.a13 = self.c13 * 2*self.teamsize
        self.w2 = self.p-self.a2
        self.w13 = self.p - self.a13
        while self.w2 < 0:
            self.c2 -= 1
            self.a2 = self.c2*2*self.teamsize
            self.w2 = self.p-self.a2
        while self.w13 < 0:
            self.c13 -= 1
            self.a13 = self.c13*2*self.teamsize
            self.w13 = self.p-self.a13
        if self.t2 == 0:
            self.c2 = self.c13
        elif self.t1 == 0 and self.t3 == 0:
            self.c13 = self.c2
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
        self.waitlist2 = []
        self.playlist2 = []
        self.waitlist3 = []
        self.playlist3 = []
        self.calc_game_counts2()
        self.g = 0

    def set_game_count(self, g):
        if g == -1:
            self.g = UNCONSTRAINED_GAME_NUMBER
            self.maxwait = UNCONSTRAINED_GAME_NUMBER
            self.appearances = self.g - self.maxwait
            self.g_list = [0, UNCONSTRAINED_GAME_NUMBER, 0]
        else:
            self.g = g
            if self.g in self.waitlist:
                self.rizemode = -1
            elif self.g in self.playlist:
                self.rizemode = 1
            elif self.g in self.waitlist2:
                self.rizemode = -2
            elif self.g in self.playlist2:
                self.rizemode = 2
            elif self.g in self.waitlist3:
                self.rizemode = -3
            elif self.g in self.playlist3:
                self.rizemode = 3
            self.players[0].wait = self.rizemode
            self.maxwait = self.maxwait_list[self.g]
            self.appearances = self.g - self.maxwait
            self.g_list = self.games_intervalwise(self.g)

        self.init_partner_matrix(first=True)
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
        # In some cases it is preferred to preserve the female-male ratio in the group of waiting people
        gender_specific = False  # For strongly differing male and female counts this is counter-productive (because then we can rarely play minority games in the end)
        if (0.6 > self.female_ratio > 0.4) and 0 == (self.teamsize % 2):
            gender_specific = True  # except for this case, then it makes sense
        ok = False
        while not ok:      # In some cases, the gender-specific selection seemed to lead to players waiting more than max_wait. I'm not sure how to fix that, so after gender-specific selection, check
                        # whether no player has more wait than max_wait. Otherwise ok is set to false. Edit: I am not sure whether this actually happens, might have been
                        # a different issue. But I leave it that way, because it is not harmful.
            ok = True
            waiting_this_turn = self.canwait(wait_request)
            wr = len(waiting_this_turn)
            male_wr = len(np.nonzero(waiting_this_turn < (self.p-self.females))[0])   # how many male players have requested to wait
            female_wr = wr - male_wr                                                  # same for female
            wmale = int(self.w*(1-self.female_ratio))-male_wr                  # how many male players still have to be selected to wait
            wfemale = int(self.w*self.female_ratio)-female_wr                  # same for female
                                                                               # In the usual case, male_wr + female_wr + wmale + wfemale = w-1 and not = w, because of the truncation
                                                                               # Thus, the last waiting player must be chosen randomly from both groups
            wrandom = self.w - wr - wmale - wfemale                            # This variable hold the number of players to choose randomly. It is either 0 or 1

            self.i += 1        # increment game counter
            done = (wr == self.w)
            while not done:
                not_waiting = np.setdiff1d(self.players.index, waiting_this_turn)
                min_wait = np.min(self.players.wait[not_waiting])
                min_indices = np.intersect1d(np.where(min_wait == self.players.wait)[0], not_waiting)
                male_min_ind = min_indices[np.nonzero(min_indices < (self.p - self.females))[0]]     # All male players that are available for waiting
                female_min_ind = min_indices[np.nonzero(min_indices >= (self.p - self.females))[0]]  # same for female
                malediff = len(male_min_ind) - wmale                                    # This is <= 0 if we can select all male players in this iteration and < 0 if we need to continue in the next
                femalediff = len(female_min_ind) - wfemale                              # Same for female
                wmale_this = min(len(male_min_ind), wmale)
                wfemale_this = min(len(female_min_ind), wfemale)
                wmale -= wmale_this
                wfemale -= wfemale_this
                # We are done after this iteration if we can select all players in this iteration: male, female and random (in case gender_specific is set)
                # Otherwise we just select randomly - with the analogue terminating condition
                if gender_specific:
                    if malediff >= 0 and femalediff >= 0:
                        if malediff+femalediff >= wrandom:
                            todo_list = ["male", "female", "random"]
                            done = True
                        else:
                            # We select both male and female, but go to the next iteration to select the random
                            todo_list = ["male", "female"]
                            pass
                    elif malediff >= 0 and femalediff < 0:
                        # If we can select all male but not all female
                        if malediff - wrandom <= 0:
                            # If we can do one random after the males and then go to the next iteration to continue
                            todo_list = ["male", "female", "random"]
                        else:
                            # If we cannot do that, it does not work out. We select randomly
                            gender_specific = False
                    elif malediff < 0 and femalediff >= 0:
                        if femalediff - wrandom <= 0:
                            todo_list = ["male", "female", "random"]
                        else:
                            gender_specific = False
                    else:
                        # We select all and then go to the next iteration
                        todo_list = ["male", "female"]

                if gender_specific:
                    for what_to_do in todo_list:
                        if what_to_do == "male":
                            if wmale_this == 0:
                                continue
                            wait_prob_male = self.players.wait_prob[male_min_ind]
                            probs_male = wait_prob_male.astype(float) / np.sum(wait_prob_male)
                            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(male_min_ind, wmale_this, replace=False, p=probs_male)))
                        elif what_to_do == "female":
                            if wfemale_this == 0:
                                continue
                            wait_prob_female = self.players.wait_prob[female_min_ind]
                            probs_female = wait_prob_female.astype(float) / np.sum(wait_prob_female)
                            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(female_min_ind, wfemale_this, replace=False, p=probs_female)))
                        elif wrandom > 0:
                            min_indices_this = np.setdiff1d(min_indices, waiting_this_turn)  # These are left from min_indices
                            if len(min_indices_this) == 0:
                                continue
                            wait_prob = self.players.wait_prob[min_indices_this]
                            probs = wait_prob.astype(float) / np.sum(wait_prob)
                            waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(min_indices_this, wrandom, replace=False, p=probs)))
                            wrandom = 0
                else:
                    # random selection
                    wdif = self.w - len(waiting_this_turn)    # We need to select the missing waiting players
                    if wdif <= len(min_indices):              # But we can select at max the number of min_indices
                        done = True
                    else:
                        wdif = len(min_indices)
                    wait_prob = self.players.wait_prob[min_indices]
                    probs = wait_prob.astype(float) / np.sum(wait_prob)
                    waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(min_indices, wdif, replace=False, p=probs)))
            # here waiting_this_turn is finished
            # we need to check if it is valid and otherwise set ok to False
            if np.any(self.players[waiting_this_turn].wait > self.maxwait):
                ok = False
                print("not ok.")


        # LEGACY:
        # noreq = np.setdiff1d(self.players.index, waiting_this_turn)
        # wdif = self.w - wr   # wdif is the number of players that still need to be selected for wait, after wait requests have been registered
        # self.i += 1  # increment game counter
        # min_wait = np.min(self.players.wait[noreq])
        # min_indices = np.intersect1d(np.where(min_wait == self.players.wait)[0], noreq)
        # if not len(min_indices) < wdif:   # we can choose all waiting players from the minimal pool
        #     # only in this case we can select by gender
        #     male_min_ind = np.nonzero(min_indices < (self.p - self.females))[0]     # All male players that are available for waiting
        #     female_min_ind = np.nonzero(min_indices >= (self.p - self.females))[0]  # same for female
        #     if not len(male_min_ind) < wmale and not len(female_min_ind) < wfemale:
        #         #TODO: It would be better to be able to select by gender also when choosing from min_indices is not enough. If we can use all players from min_indices and still conform with the ratio, we are fine!
        #         # Here we can do selection by gender
        #         #Select male players for waiting
        #         wait_prob_male = self.players.wait_prob[male_min_ind]
        #         probs_male = wait_prob_male.astype(float) / np.sum(wait_prob_male)
        #         waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(male_min_ind, wmale, replace=False, p=probs_male)))
        #         # Select female players for waiting
        #         wait_prob_female = self.players.wait_prob[female_min_ind]
        #         probs_female = wait_prob_female.astype(float) / np.sum(wait_prob_female)
        #         waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(female_min_ind, wfemale, replace=False, p=probs_female)))
        #         wdif = self.w - len(waiting_this_turn)   # usually we need one player more (because wmale and wfemale do not add up to wdif
        #     if wdif != 0:
        #         if not wdif == 1:
        #             print("WARNING. wdif is {}, but should be 1.".format(wdif))
        #         # Here we do random selection, because it did not work by gender
        #         # Also, we randomly select the last player if wmale and wfemale did not add up to wdif
        #         wait_prob = self.players.wait_prob[min_indices]
        #         probs = wait_prob.astype(float) / np.sum(wait_prob)
        #         waiting_this_turn = np.concatenate((waiting_this_turn, np.random.choice(min_indices, wdif, replace=False, p=probs)))
        # else:
        #     waiting_this_turn = np.concatenate((waiting_this_turn, min_indices))
        #     other_indices = np.setdiff1d(self.players.index[noreq], min_indices)
        #
        #     wait_prob = self.players.wait_prob[other_indices]
        #     probs = wait_prob.astype(float) / np.sum(wait_prob)
        #     waiting_this_turn = np.concatenate(
        #         (waiting_this_turn, np.random.choice(other_indices, wdif - len(min_indices), replace=False, p=probs)))



        self.players.wait[waiting_this_turn] += 1
        #update waiting probabilities: reduce for players that waited, increase for players that played.
        playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)
        if self.p > self.w*2:
            self.players.wait_prob[waiting_this_turn] = 0
            self.players.wait_prob[playing_this_turn] += 1
            self.players["wait_prob"] = np.clip(self.players.wait_prob, 0, 4)
        else:
            self.players.wait_prob[waiting_this_turn] -= 1
            self.players.wait_prob[playing_this_turn] += 2
            self.players["wait_prob"] = np.clip(self.players.wait_prob, 1, 4)

        # MAKING TEAMS (OLD METHOD)
        # playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)    # all that are not waiting
        # np.random.shuffle(playing_this_turn)                                        # shuffle them
        # # make teams of consecutive players in shuffled list
        # team_indices = np.array([[a, b] for a, b in zip(playing_this_turn[::2], playing_this_turn[1::2])])
        # teams = self.players[team_indices]

        # MAKING TEAMS (NEW METHOD) playing partner matrix is used for teamsize 2. Otherwise teams are unconstrained random.
        if self.teamsize == 2:
            if 0 == len(np.where(self.partner_matrix == 0)[0]):  # if partner matrix all 1, reset it
                self.init_partner_matrix(first=True)
                ret = 1
            teams_ready = False
            tries = TRIES    #in case matching cannot be found, but should theoretically be possible, try again that number of times before irregularly resetting partner matrix
            while not teams_ready:
                playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)  # all that are not waiting
                playing_partner_matrix = self.partner_matrix[playing_this_turn][:, playing_this_turn]
                playing_minor_matrix = self.minor_partner_matrix[playing_this_turn][:, playing_this_turn]
                playing_minor_mask = self.minor_mask[playing_this_turn][:, playing_this_turn]
                team_indices = []
                teams_ready = True
                partner_matrix_temp = np.array(self.partner_matrix)
                minor_matrix_temp = np.array(self.minor_partner_matrix)
                if self.i - 1 >= self.second_half_start:
                    # If we are in second half
                    playing_partner_matrix_stored = playing_partner_matrix    # store original matrix. We need it again when we are finished with building minority teams (NOT SURE YET)
                    playing_partner_matrix_minored = np.logical_and(playing_partner_matrix, playing_minor_matrix)         # load actual partner matrix from minor matrix (in first "half" the minority part is set to 1
                    playing_partner_matrix_masked = np.logical_or(playing_partner_matrix_minored, playing_minor_mask)     # temporarily mask the non-minority part with ones to build minority teams
                    playing_partner_matrix = playing_partner_matrix_masked
                    if self.female_ratio < 0.5:
                        num_min = np.count_nonzero(playing_this_turn >= (self.p-self.females))
                    else:    # here ratio is > 0.5 because we don't get into second half when it is == 0.5
                        num_min = np.count_nonzero(playing_this_turn < (self.p-self.females))
                    minor_teams = num_min // (2 * self.teamsize) * 2
                for ti in range(2*self.c):  # ti = team index
                    if self.i - 1 >= self.second_half_start:
                        if ti == minor_teams:
                            # continue with normal team building. It is important to note that this only happens once, at the exact first index where team building is reverted to majority again
                            playing_partner_matrix = playing_partner_matrix_stored     #reset to original matrix in which minority part is set to 1
                    counts = np.array([len(row)-np.count_nonzero(row) for row in playing_partner_matrix])
                    counts[np.nonzero(counts == 0)] = 1000     #shift zero values to the back
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
                        if tries == 0:
                            self.init_partner_matrix(first=True)
                            ret = 2
                        else:
                            tries -= 1
                        teams_ready = False
                        break
                    choice = np.random.choice(zero_entries_indices)
                    # get partner for pl
                    par = playing_this_turn[choice]
                    # set corresponding indices in partner_matrix to 1
                    partner_matrix_temp[pl, par] = 1
                    partner_matrix_temp[par, pl] = 1
                    if self.i - 1 >= self.second_half_start:
                        minor_matrix_temp[pl, par] = 1
                        minor_matrix_temp[par, pl] = 1
                    # now delete also pl's row from temp matrix
                    playing_partner_matrix = np.delete(playing_partner_matrix, pid, axis=0)
                    # and delete par's row and column and delete par from playing_this_turn
                    playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=0)
                    playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=1)
                    playing_this_turn = np.delete(playing_this_turn, choice)
                    if self.i - 1 >= self.second_half_start:
                        # delete rows and columns also in stored matrix. This matrix is restored after all minor teams have been composed
                        playing_partner_matrix_stored = np.delete(playing_partner_matrix_stored, pid, axis=0)
                        playing_partner_matrix_stored = np.delete(playing_partner_matrix_stored, pid, axis=1)
                        playing_partner_matrix_stored = np.delete(playing_partner_matrix_stored, choice, axis=0)
                        playing_partner_matrix_stored = np.delete(playing_partner_matrix_stored, choice, axis=1)
                    # add team to teams list
                    team_indices.append([pl, par])
                # Check here whether minority teams are adjacent in mmr list and they would be matched together on one court
                # Otherwise try again. If tries == 0, shift second half to a later game and restart team building without minors
                if teams_ready and self.matchmaking:
                    if self.i - 1 >= self.second_half_start and minor_teams > 0:
                        teams = self.players[np.array(team_indices)]
                        temp_mmr = np.sum(teams.mmr.astype(float), axis=1)  # calculate match-making-ratio for each team
                        temp_mmr_sorted_indices = np.argsort(temp_mmr)[::-1]
                        minor_indices = np.nonzero(np.isin(temp_mmr_sorted_indices, np.arange(minor_teams)))[0]     # Get indices of minor teams in mmr sorted list
                        even_teams = minor_indices[::2]       # if we make pairs of teams, these are the first teams of these pairs
                        if not np.all(np.mod(even_teams, 2) == 0):     # The first teams of these pairs must have an even index to be matched with the second teams
                            teams_ready = False
                        odd_teams = minor_indices[1::2]
                        if not (odd_teams - 1) == even_teams:         # Make sure the "odd" teams come directly after the respective "even" team
                            teams_ready = False
                        if not teams_ready:
                            if tries == 0:
                                self.second_half_start = self.i
                                tries = TRIES
                            else:
                                tries -= 1
            team_indices = np.array(team_indices)
            self.partner_matrix = np.array(partner_matrix_temp)
            self.minor_partner_matrix = np.array(minor_matrix_temp)
        else:
            # TODO: There is a special case: If ratio == 0.5 and teamsize even, we can play with evenly mixed teams. I am not sure if it is worth implementing that, though.
            playing_this_turn = np.setdiff1d(self.players.index, waiting_this_turn)  # all that are not waiting
            team_indices = np.random.permutation(playing_this_turn).reshape((2*self.c, self.teamsize))
        teams = self.players[team_indices]

        # MATCHMAKING
        if self.matchmaking:
            temp_mmr = np.sum(teams.mmr.astype(float), axis=1)    # calculate match-making-ratio for each team
            temp_mmr_sorted_indices = np.argsort(temp_mmr)[::-1]
            teams_sorted = teams[temp_mmr_sorted_indices]     # descendingly sorted by mmr (strongest come first).
        else:
            teams_sorted = teams
        self.games.append(teams_sorted.index)

        self.state = 1
        with open("saved.p", 'wb') as f:
            pickle.dump(self, f)

        return ret

    def init_partner_matrix(self, first=False):
        self.partner_matrix = np.eye(self.p)
        if self.females:  # if female players are in the game
            if self.female_ratio < 0.5:
                # prevent w/w games
                self.partner_matrix[-self.females:, -self.females:] = np.ones((self.females, self.females))
                if first:
                    self.second_half_start = max(int(np.ceil(self.g / 2)), self.g - self.females + 1)  # from this game on, w/w games are generated and played if adjacent in MMR list
                    self.minor_partner_matrix = np.eye(self.p)
                    self.minor_mask = np.ones((self.p, self.p))
                    self.minor_mask[-self.females:, -self.females:] = np.zeros((self.females, self.females))
            elif self.female_ratio > 0.5:
                # prevent m/m games
                self.partner_matrix[:-self.females, :-self.females] = np.ones((self.p - self.females, self.p - self.females))
                if first:
                    self.second_half_start = max(int(np.ceil(self.g / 2)), self.g - (self.p - self.females) + 1)  # from this game on, m/m games are generated and played if adjacent in MMR list
                    self.minor_partner_matrix = np.eye(self.p)
                    self.minor_mask = np.ones((self.p, self.p))
                    self.minor_mask[:-self.females, :-self.females] = np.zeros((self.p - self.females, self.p - self.females))
            else:
                # evenly matched numbers of male / female players
                # only allow mixed games
                self.partner_matrix[-self.females:, -self.females:] = np.ones((self.females, self.females))
                self.partner_matrix[:-self.females, :-self.females] = np.ones((self.p - self.females, self.p - self.females))
                if first:
                    self.second_half_start = self.g  # no second half. we can always play mixed (At least in case of even team size)
                    self.minor_partner_matrix = np.eye(self.p)
                    self.minor_mask = np.zeros((self.p, self.p))
        else:
            if first:
                self.second_half_start = self.g  # no second half. we can always play mixed (At least in case of even team size)
                self.minor_partner_matrix = np.eye(self.p)
                self.minor_mask = np.zeros((self.p, self.p))

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
        teams_sorted = self.players[team_indices_sorted]
        team_mmr = np.sum(teams_sorted.mmr.astype(float), axis=1)  # we use sum here because, we suppose a player is expected to score x points when his mmr is x. Thus, to calculate expected result, MMRs are summed up.
        self.results[game_number] = res
        for ci, court_results in enumerate(self.results[game_number]):  # ci = court index
            cumdiff = 0
            for set_result in court_results:   # si = set index
                pl = self.players[team_indices_sorted[2 * ci:2 * ci + 2]]  # I know the values are copied here, but I buy myself readability in mmr lines by keeping them short and pay with efficiency
                score1 = set_result[0]
                score2 = set_result[1]
                scorediff = score1-score2
                maxpoints = max(score1, score2)
                cumdiff += scorediff

                for pi in range(self.teamsize):
                    # generate index 0: lost, 1: draw, 2: won. index default score array with that index
                    self.players[team_indices_sorted[2 * ci, pi]].score += [0, 0, 1][np.sign(scorediff) + 1]
                    self.players[team_indices_sorted[2 * ci + 1, pi]].score += [0, 0, 1][np.sign(-scorediff) + 1]

                    # difference is from the POV of team 1, so positive if team 1 won
                    self.players[team_indices_sorted[2 * ci, pi]].diff += scorediff
                    self.players[team_indices_sorted[2 * ci + 1, pi]].diff -= scorediff

                    self.players[team_indices_sorted[2 * ci, pi]].points += score1
                    self.players[team_indices_sorted[2 * ci + 1, pi]].points += score2

                    mmr_diff = team_mmr[2 * ci + 1] - team_mmr[2 * ci]  # This is the other direction than scorediff. When scorediff and mmr_diff are added, values are higher in case of a surprising result

                    sign_1 = [-1, 0, 1][np.sign(scorediff) + 1]     # result (win:1, draw:0, loss:-1) from the perspective of team1
                    sign_2 = [-1, 0, 1][np.sign(-scorediff) + 1]    # same for team2

                    mmr_sign_1 = [-1, 0, 1][int(np.sign(mmr_diff)) + 1]

                    streak_1 = [0.3, 0.6, 1][pl[0,pi].mmr_tag_w] if scorediff > 0 else [0.3, 0.6, 1][pl[0,pi].mmr_tag_l]
                    streak_2 = [0.3, 0.6, 1][pl[1,pi].mmr_tag_w] if scorediff < 0 else [0.3, 0.6, 1][pl[1,pi].mmr_tag_l]

                    pred_corr_discount = PRED_CORR_DISCOUNT

                    if mmr_sign_1 * sign_1 < 0:
                        # win/loss prediction correct
                        # mmr_diff has different sign than scorediff, meaning that the results is as predicted
                        # in case MMR difference taken into account, the correction rate is lower because the overall prediction was correct
                        if not self.matchmaking[0]:
                            if not self.matchmaking[1]:
                                # simplest method. Just bonus/malus of 1
                                correction_term = 1
                            else:
                                # similar, but discounted because prediction was right
                                correction_term = pred_corr_discount
                        else:
                            if not self.matchmaking[1]:
                                correction_term = abs(scorediff)
                            else:
                                # if the winner performed better than expected (scorediff + mmr_diff < 0), they get a bonus, if worse than expected they get a malus.
                                # same for the looser.
                                correction_term = np.sign(scorediff) * (scorediff + mmr_diff) * pred_corr_discount
                                if maxpoints*pred_corr_discount < abs(correction_term):
                                    # maxpoints is the number of points the winner scored. mmr cannot be corrected by more than that
                                    correction_term = maxpoints*pred_corr_discount * np.sign(correction_term)
                    else:
                        # win/loss prediction incorrect (or prediction and/or result is a draw
                        # SURPRISE!
                        # Team that wins gets all the points, team that looses gets the same amount subtracted
                        if not self.matchmaking[0]:
                            if not self.matchmaking[1]:
                                correction_term = 1
                            else:
                                correction_term = min(maxpoints, abs(mmr_diff))
                        else:
                            if not self.matchmaking[1]:
                                correction_term = abs(scorediff)
                            else:
                                correction_term = min(maxpoints, abs(scorediff + mmr_diff))

                    self.players[team_indices_sorted[2 * ci, pi]].mmr += sign_1 * (correction_term / self.teamsize) * [1, streak_1][self.matchmaking[2]]
                    self.players[team_indices_sorted[2 * ci + 1, pi]].mmr += sign_2 * (correction_term / self.teamsize) * [1, streak_2][self.matchmaking[2]]

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
        for pli in range(self.teamsize):
            self.players[teams[2 * ci, pli]].mmr_tag_w += 1 if diff > 0 else -1
            self.players[teams[2 * ci + 1, pli]].mmr_tag_w += 1 if diff < 0 else -1

            self.players[teams[2 * ci, pli]].mmr_tag_l += 1 if diff < 0 else -1
            self.players[teams[2 * ci + 1, pli]].mmr_tag_l += 1 if diff > 0 else -1

        for ti in range(0, 2):     #truncating on interval [0,2]
            for pi in range(0, self.teamsize):
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
