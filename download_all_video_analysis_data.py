
import sqlite3
import time
from get_reply import fetch_and_save_comments
from get_danmaku import fetch_and_save_danmaku

# 连接数据库
conn = sqlite3.connect('bilibili.db')
cursor = conn.cursor()

# 从ranking表中依次取100条数据，读取bvid
for i in range(100):
    cursor.execute("SELECT bvid FROM ranking LIMIT 1 OFFSET ?", (i,))
    bvid = cursor.fetchone()[0]
    print(bvid)
    fetch_and_save_comments(bvid)
    fetch_and_save_danmaku(bvid)

conn.close()