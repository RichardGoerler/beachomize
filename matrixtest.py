import numpy as np
import pdb

p = 7
w = 3
c = 1

partner_matrix = np.zeros((p, p))

for ii in range(10):
    waiting_this_turn = np.random.choice(range(p), w, replace=False)
    playing_this_turn = np.setdiff1d(np.arange(7), waiting_this_turn)

    playing_partner_matrix = partner_matrix[playing_this_turn][:, playing_this_turn]

    teams = []

    for ci in range(c):
        for ti in range(2):   # ti = team index
            print("ci = {}, ti = {}".format(ci, ti))
            # pdb.set_trace()
            # choose random player
            pid = np.random.randint(len(playing_this_turn))
            pl = playing_this_turn[pid]
            # delete pl's column from temp matrix and delete pl from playing_this_turn
            playing_partner_matrix = np.delete(playing_partner_matrix, pid, axis=1)
            playing_this_turn = np.delete(playing_this_turn, pid)
            # get player's row from matrix
            player_row = playing_partner_matrix[pid, :]
            # get indices of still zero entries and select one at random
            zero_entries_indices = np.where(player_row == 0)[0]
            choice = np.random.choice(zero_entries_indices)
            # get partner for pl
            par = playing_this_turn[choice]
            # set corresponding indices in partner_matrix to 1
            partner_matrix[pl, par] = 1
            partner_matrix[par, pl] = 1
            # now delete also pl's row from temp matrix
            playing_partner_matrix = np.delete(playing_partner_matrix, pid, axis=0)
            # and delete par's row and column and delete par from playing_this_turn
            playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=0)
            playing_partner_matrix = np.delete(playing_partner_matrix, choice, axis=1)
            playing_this_turn = np.delete(playing_this_turn, choice)
            # add team to teams list
            teams.append([pl, par])

    print('')
    print(ii)
    print('')
    print(teams)
    print('')
    print(partner_matrix)
