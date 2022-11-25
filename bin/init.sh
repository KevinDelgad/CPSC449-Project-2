#!/bin/sh

sqlite3 ./var/primary/mount/game.db < ./share/game.sql
sqlite3 ./var/user.db < ./share/user.sql
python3 dbpop.py
