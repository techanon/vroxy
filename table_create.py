import sqlite3
conn = sqlite3.connect("cache.db")
c = conn.cursor()
c.execute('''CREATE TABLE id_cache (type,contentid,url,date,unique (type,contentid))''') # Type = YouTube, Twitch, etc.  ContentID = UUID for videos / streams Date = Date the entry was last updated or inserted. Unique constraints to one entry per service / uuid combo.
conn.commit()
conn.close()
print('Created the cache db')