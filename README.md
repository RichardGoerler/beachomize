[Official Website](http://beachomize.de)
========================================
beachomize
==========
Software for organizing shuffled beach volleyball tournaments with a matchmaking algorithm. Implemented in python and tkinter.

![main_example](http://beachomize.de/image/main_example.png)

### Game mode
#### Shuffling
In each round, teams of two are randomly formed.
#### Matchmaking
After creating teams, fixtures are set based on MMR (match making rating) of each player. The team with the best average MMR plays against the second-best. MMRs are updated after each game.

Features
--------
### Customize your tournament
![welcome](http://beachomize.de/image/welcome1.png)

Set number of courts, time and duration, and matchmaking method. For the case that not all courts are available all the time, three time intervals with two different court counts can be defined.
### Handle any number of players (odd / prime)
![game_number](http://beachomize.de/image/game_number1.png)

Get suggestions for number of games to play. Adjust the game number by letting player 1 run "outside the competition".
### Let players request to wait
![wait_select](http://beachomize.de/image/wait_select.png)

Usually the players that wait are randomly determined each round, but players can also request to skip a round.
### Non-repeating team compositions
As long as it is possible, no player will have the same teammate twice.
### Adjust appearance
![settings](http://beachomize.de/image/settings1.png)
### Auto-save
The state of the tournament is automatically saved on the hard drive to avoid data loss, for example when the window is closed accidentially. The most recent auto-save can be loaded on start-up.
### Localization
Language files can be added. Currently English and German are available.

Installation
------------
Download the [latest release](https://github.com/RichardGoerler/beachomize/releases) or clone the [git repository](https://github.com/RichardGoerler/beachomize).
### Prerequisites
In order to run **beachomize** you need to have python installed on your machine. python2 is recommended, but it should also run work python3. The python packages tkinter and numpy are required.
#### Install python2, tkinter and numpy
##### Linux
Use your package manager to install the packages *python*, *python-tk* and *python-numpy*
For instance, on Ubuntu **sudo apt-get install python python-tk python-numpy** should work in most cases.
##### Windows
On Windows, *Anaconda* is usually the way to run python. You can download the windows version [here](https://www.continuum.io/downloads#windows). In that installation, the required packages should already be included.

Usage
-----
Before starting your tournament, make sure you place you player names in the file *players.txt*. Each line should consist of a player name and the initial MMR of that player (default 0).  
You can also customize the court names and sorting by editing the file *courts.txt*. Delete the file to use default numbering.

In your anaconda or linux console, navigate to the **beachomize** directory and type **python gui&#46;py**

To change the language, edit the file *\__init\__.py* in the *lang*-directory. Replace **eng** with the language of your choice. A python-file with that name, defining all necessary constants, has to be present in the *lang*-folder.

Contact
-------
Richard Görler, Hattingen, Germany  
richard.goerler[at]gmail&#46;com
