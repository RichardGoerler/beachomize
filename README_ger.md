[README in English](https://github.com/RichardGoerler/beachomize/blob/master/README.md)

beachomize
==========
Manager für Beachvolleyball-Turniere mit zufälligen Teams und einem Matchmaking-Algorithmus. Implementiert in Python und Tkinter.

![main_example](https://beachomize.de/image/main_example_ger.png)

### Spielmodus
#### Zufällige Teams
In jeder Runde werden neue Teams zufällig gebildet.
#### Matchmaking
Spielpaarungen werden auf Basis der Spielstärkewerte (MMR - match making rating) der Spieler festgelegt. Das Team mit der höchsten durchschnittlichen Spielstärke spielt gegen das zweitbeste. Spielstärkewerte werden nach jedem Spiel aktualisiert.

Funktionen
--------
### Turnier-Einstellungen
![welcome](https://beachomize.de/image/welcome_ger1.png)

Anzahl der Felder, Teamgröße, Startzeit und Dauer, und die Art des Matchmakings sind wählbar. Falls nicht alle Felder über die gesamte Dauer des Turniers zur Verfügung stehen, können drei Zeitintervalle mit zwei verschiedenen Feld-Anzahlen definiert werden.
### Beliebige Anzahl an Spielern (auch ungerade oder prim)
![game_number](https://beachomize.de/image/game_number_ger1.png)

Es werden Vorschläge für die Anzahl der zu spielenden Spiele berechnet. Wenn Spieler 1 außer Konkurrenz bleibt, ist die Anzahl der Spiele flexibler.
### Spieler können auf Wunsch pausieren
![wait_select](https://beachomize.de/image/wait_select.png)

Normalerweise werden die aussetzenden Spieler zufällig bestimmt, aber es ist auch möglich, diese manuell zu wählen.
### Team-Zusammensetzungen wiederholen sich nicht
Solange es möglich ist, bekommt kein Spieler denselben Mitspieler zweimal. Gilt nur für Zweierteams.
### Einstellbare Text- und Tabellengröße
![settings](https://beachomize.de/image/settings_ger.png)
### Automatisches Speichern
Der Turnierstatus wird automatisch gespeichert um Datenverlust zu verhindern, z.B. wenn das Programm aus Versehen geschlossen wird. Beim Programmstart kann das letzte Turnier geladen werden.
### Sprache
Sprachdateien können hinzugefügt werden. Aktuell sind Deutsch und Englisch verfügbar.

Installation
------------
[Latest release](https://github.com/RichardGoerler/beachomize/releases) herunterladen oder das [git repository](https://github.com/RichardGoerler/beachomize) klonen.
### Systemvoraussetzungen
Um **beachomize** zu verwenden, muss Python installiert sein. Python2 ist empfohlen, aber es sollte auch mit Python3 funktionieren. Die Python-Pakete Tkinter und Numpy werden benötigt.
#### Installation von Python2, Tkinter and Numpy
##### Linux
Paketmanager verwenden, um die Pakete *python*, *python-tk* und *python-numpy* zu installieren.
Unter Ubuntu z.B. sollte **sudo apt-get install python python-tk python-numpy** in den meisten Fällen funktionieren.
##### Windows
Unter Windows wird üblicherweise *Anaconda* verwendet, um Python zu installieren. Die Windows-Version gibt es [hier](https://www.continuum.io/downloads#windows). In dieser Installation sollten die benötigten Pakete bereits enthalten sein.

Verwendung
-----
Vor dem Turnier müssen die Namen der teilnehmenden Spieler in die Datei *players.txt* eingetragen werden. Dabei sollte jede Zeile den Namen eines Spielers enthalten, optional gefolgt von der initialen Spielstärke des Spielers (standardmäßig 0).
Durch Bearbeiten der Datei *courts.txt* können auch die Namen der Spielfelder eingestellt werden. Fehlt die Datei, werden die Felder einfach durchnummeriert.

Starten des Programms: Im Anaconda- oder Linux-Terminal zum **beachomize**-Verzeichnis wechseln und **python gui&#46;py** eingeben.

Um die Sprache zu ändern, muss die Datei *\_\_init\_\_.py* im *lang*-Verzeichnis editiert und **eng** durch ein anderes Kürzel (z.B. **ger**) ersetzt werden. Eine python-Datei mit demselben Namen, die alle notwendigen Konstanten definiert, muss im *lang*-Ordner liegen.

Kontakt
-------
Richard Görler, Hattingen  
richard.goerler[at]gmail&#46;com
