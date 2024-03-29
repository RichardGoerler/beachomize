[README auf Deutsch](https://github.com/RichardGoerler/beachomize/blob/master/README_ger.md)

beachomize
==========
Software for organizing shuffled beach volleyball tournaments with a matchmaking algorithm. Implemented in Python and Tkinter.

![main_example](https://drive.google.com/uc?export=download&id=1cazkhPI0yIkikSYS4OV3AdZZrIzxfh2P)

### Game mode
#### Shuffling
In each round, teams are randomly formed.
#### Matchmaking
After creating teams, fixtures are set based on MMR (match making rating) of each player. The team with the best average MMR plays against the second-best. MMRs are updated after each game.

Features
--------
### Customize your tournament
![welcome](https://drive.google.com/uc?export=download&id=1D6ntZGc2uNoURCeuz149HdSqn8XsYLaB)

Set number of courts, team size, time and duration, and matchmaking method. For the case that not all courts are available all the time, three time intervals with two different court counts can be defined.
### Handle any number of players (odd / prime)
![game_number](https://drive.google.com/uc?export=download&id=1wZafAKZSsYBJMVZ5TEzniqYxzaSDEBfR)

Get suggestions for number of games to play. Adjust the game number by letting player 1 run "outside the competition".
### Let players request to wait
![wait_select](https://drive.google.com/uc?export=download&id=1Vp_i3ig8NhhKRuE6mYN4h1jUuE6aoPPr)

Usually the players that wait are randomly determined each round, but players can also request to skip a round.
### Non-repeating team compositions
As long as it is possible, no player will have the same teammate twice. Works only for teams of two.
### Adjust appearance
![settings](https://drive.google.com/uc?export=download&id=1bhnWq-dfHTIyke0wQ1qOwjZBQucMlZ5F)
### Auto-save
The state of the tournament is automatically saved on the hard drive to avoid data loss, for example when the window is closed accidentally. The most recent auto-save can be loaded on start-up.
### Localization
Language files can be added. Currently English and German are available.

Installation
------------
Download the [latest release](https://github.com/RichardGoerler/beachomize/releases) or clone the [git repository](https://github.com/RichardGoerler/beachomize).
### Prerequisites
In order to run **beachomize** you need to have Python installed on your machine. The python packages Tkinter and Numpy are required.
#### Install Python3, Tkinter and Numpy
##### Linux
Use your package manager to install the packages *python3*, *python3-tk* and *python3-numpy*
For instance, on Ubuntu **sudo apt-get install python3 python3-tk python3-numpy** should work in most cases.
##### Windows
On Windows, *Anaconda* is usually the way to run python. You can download the windows version [here](https://www.continuum.io/downloads#windows). In that installation, the required packages should already be included.

Usage
-----
Before starting your tournament, make sure you place your player names in the file *players.txt*. Each line should consist of a player name and optionally the initial MMR of that player (default 0).  
You can also customize the court names and sorting by editing the file *courts.txt*. Delete the file to use default numbering.

In your Anaconda or Linux terminal, navigate to the **beachomize** directory and type **python gui&#46;py** or **python3 gui&#46;py**, depending on your installation type.

To change the language, edit the file *\_\_init\_\_.py* in the *lang*-directory. Replace **eng** with the language of your choice. A python-file with that name, defining all necessary constants, has to be present in the *lang*-folder.

Contact
-------
Richard Görler, Hattingen, Germany  
richard.goerler[at]gmail&#46;com
