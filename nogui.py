# -*- coding: utf-8 -*-

import numpy as np

FILENAME = "players.txt"

def _split_result(str):
    res = [int(i3) for j3 in [s3.split() for s3 in [i2 for j2 in [s2.split('-') for s2 in [i1 for j1 in
                [s1.split(',') for s1 in str.split('/')] for i1 in j1]] for i2 in j2]] for i3 in j3 if i3.isdigit()]
            #got that from the internet, did not understand it but it works
            #http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return res

def out_court_number_changed(c):
    print("Anzahl der Felder korrigiert auf {}.".format(c))

def out_player_count(p):
    print("{} Spieler registriert.".format(p))

def out_game_count(g,rizemode):
    print("Anzahl der Spiele auf {} gesetzt. Rizemode auf {} gesetzt.".format(g, rizemode))

def out_schedule(timeframe, orgatime, schedule):
    print(
    "Zeit für jedes Spiel: {} Minuten + {} Minuten Organisation.".format(timeframe - orgatime, orgatime))
    print("Spielplan:")
    for i, t in enumerate(schedule):
        print("Spiel {}: {:02d}:{:02d} Uhr".format(i + 1, t / 100, t % 100))

def out_game_announce_time(timeframe, orgatime, schedule, g, i):
    print("Erstelle Spiel Nummer {}.".format(i + 1))
    hour = schedule[i] / 100
    minute = schedule[i] % 100
    minute += timeframe - orgatime
    while minute > 60:
        hour += 1
        minute -= 60
    print("Planmäßig {:02d}:{:02d} - {:02d}:{:02d} Uhr".format(schedule[i] / 100, schedule[i] % 100, hour, minute))
    if i == g - 1:
        print("Dies ist das letzte Spiel!")

def out_game_announce_teams(players_sorted, mmr_sorted=None):
    print("")
    if mmr_sorted is not None:
        for i in range(0, len(players_sorted), 2):
            mmr1 = "{:2.1f}".format(mmr_sorted[i])
            mmr2 = "{:2.1f}".format(mmr_sorted[i + 1])
            print("Feld {}: {:>7} / {:<7} {:>4} - {:<4} {:>7} / {:<7}".format([2, 1, 3][i / 2], players_sorted.name[i, 0],
                                                                              players_sorted.name[i, 1], "(" + mmr1 + ")",
                                                                              "(" + mmr2 + ")",
                                                                              players_sorted.name[i + 1, 0],
                                                                              players_sorted.name[i + 1, 1]))
    else:
        for i in range(0, len(players_sorted), 2):
            print("Feld {}: {:>7} / {:<7} - {:>7} / {:<7}".format([2, 1, 3][i / 2], players_sorted.name[i, 0], players_sorted.name[i, 1],
                                                                  players_sorted.name[i + 1, 0], players_sorted.name[i + 1, 1]))
    print("")

def out_stats(players, rize=True, final=False):
    sort_indices = np.lexsort((-players.points, -players.diff, -players.score))
    stats_sorted = players[sort_indices]
    if final:
        print("")
        print("============ENDERGEBNIS=============")
    print("")
    print("{:<8} {:<8} {:<8} {:<8}".format("Spieler", "Sätze", "Diff", "Punkte"))
    print("")
    for pl in stats_sorted:
        if (not rize) and (pl.name.lower().startswith("rize")):
            continue
        print("{:<8} {:<8} {:<8} {:<8}".format(pl.name, pl.score / 2, pl.diff, pl.points))
    print("")

def out_reset_partner_matrix_error():
    print("Erstellen von Teams Fehlgeschlagen. Partner-Matrix wird vorzeitig zurückgesetzt.")

def out_reset_partner_matrix():
    print("Teamrotation komplett. Partner-Matrix wird planmäßig zurückgesetzt.")

def in_players():
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

def in_game_count(goodlist, waitlist, playlist):
    print("Mögliche Anzahl an Spielen:")
    print("Regulär: {} , Rize wartet eins mehr: {} , Rize spielt eins mehr: {}".format(goodlist, waitlist, playlist))
    g = int(raw_input("Wie viele Spiele sollen gespielt werden?\n"))  # python2.7
    return g

def in_results(c, players_sorted):
    entered = 0
    res = [[]] * c
    while entered < len(players_sorted) / 2:
        for ci in range(len(players_sorted) / 2):  # ci = court index
            if not [] == res[ci]:  # was already entered
                continue
            result_string = raw_input(
                "Ergebnis für Spiel {:>7} / {:<7} - {:>7} / {:<7}: ".format(players_sorted.name[2 * ci, 0],
                                                                            players_sorted.name[2 * ci, 1],
                                                                            players_sorted.name[2 * ci + 1, 0],
                                                                            players_sorted.name[2 * ci + 1, 1]))  # python2.7
            res_numbers = _split_result(result_string)
            cnt = len(res_numbers)
            if (not 0 == cnt) and (2 * (cnt / 2) == cnt):  # if cnt > 0 and even number
                res[ci] = [[]] * (cnt / 2)  # in list for court make one list for each set played
                for si in range(cnt / 2):  # si = set index
                    score1 = res_numbers[2 * si]
                    score2 = res_numbers[2 * si + 1]
                    res[ci][si] = [score1, score2]
                entered += 1
    return res