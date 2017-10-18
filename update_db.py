import ConfigParser
import sqlite3

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    db_path = config.get('database', 'auto_close')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # c.execute('''UPDATE races SET closed=? WHERE raceID=?''', (0, 10452))
    c.execute('''ALTER TABLE races ADD closed_notified INTEGER''')
    conn.commit()
