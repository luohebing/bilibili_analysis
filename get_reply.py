import sqlite3
import requests
import config

def fetch_and_save_comments(bvid):
    # 连接到数据库
    conn = sqlite3.connect('bilibili.db')

    # 检索aid
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    # 遍历结果，查找以 "ranking" 为前缀的表名
    for table in cur.fetchall():
        table_name = table[0]
        if table_name.startswith("ranking"):
            print("Found table:", table_name)
            cur.execute(f"SELECT * FROM {table_name} WHERE bvid=?", (bvid,))
            aid = cur.fetchone()
            if aid:
                break

    # cur.execute("SELECT aid FROM ranking WHERE bvid = ?", (bvid,))
    # aid = cur.fetchall()
    if not aid:  # 如果在 ranking 表中没有找到 aid
        cur.execute("SELECT aid FROM specific_video WHERE bvid = ?", (bvid,))
        aid = cur.fetchall()
    
    # 创建表格
    table_name = f'bvid_{bvid}_reply'
    cur.execute(f'DROP TABLE IF EXISTS {table_name}')  # 清空表格
    cur.execute(f'CREATE TABLE {table_name} (comment TEXT, likes INTEGER)')
    
    # 发送请求获取评论信息，并保存到数据库中
    for page in range(1, 21):  # 读取20页评论
        url = 'https://api.bilibili.com/x/v2/reply'
        params = {
            'type': 1,  # 评论区类型代码
            'oid': aid,  # 视频的 aid
            'sort': 1,  # 按热度排序
            'ps': 10,   # 每页10条评论
            'pn': page,  # 当前页码
            'nohot': 0  # 显示热评
        }
        headers = config.headers
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        # 提取评论并保存到数据库
        comments = data['data']['replies']
        for comment_info in comments:
            comment = comment_info['content']['message']
            likes = comment_info['like']
            cur.execute(f"INSERT INTO {table_name} (comment, likes) VALUES (?, ?)", (comment, likes))
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()

# 示例使用
# bvid = 'BV1kU421d7YH'  # 视频的 aid
# fetch_and_save_comments(bvid)