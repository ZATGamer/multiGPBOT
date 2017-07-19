import sqlite3
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('./config.ini')

db_path = config.get('database', 'auto_close')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# c.execute('''DELETE FROM races WHERE raceID=9558''')
# c.execute('''DELETE FROM races WHERE raceID=9451''')
# conn.commit()

c.execute('''INSERT INTO races (raceID, max_pilots, notified) VALUES(?,?,?)''', (9558, 16, False))
conn.commit()

# c.execute('''INSERT INTO races (raceID, max_pilots, notified) VALUES(?,?,?)''', (9451, 10, False))
# conn.commit()

# c.execute('''UPDATE races SET max_pilots=9 WHERE raceID=9451''')
# conn.commit()
c.execute('''SELECT * FROM races''')
data = c.fetchall()
for crap in data:
    print crap

conn.close()