import sqlite3
import json
conn = sqlite3.connect('var/primary/mount/game.db')
c = conn.cursor()


f = open('share/valid.json')
data = json.load(f)

for val in data:
    c.execute("INSERT INTO valid_word (valword) VALUES(?)" , (val,)) 
f.close()   


s = open('share/correct.json')
data = json.load(s)

for val in data:
    c.execute("INSERT INTO answer (answord) VALUES(?)" , (val,))

s.close()   

conn.commit()