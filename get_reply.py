import sqlite3
import requests
import config

def fetch_and_save_comments(bvid, cookie):
    # 连接到数据库
    conn = sqlite3.connect('bilibili.db')
    cur = conn.cursor()

    # 检索aid
    cur = conn.cursor()
    cur.execute("SELECT aid FROM ranking WHERE bvid = ?", (bvid,))
    aid = cur.fetchall()
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'Cookie': cookie  # 使用 Cookie 认证
        }
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
# fetch_and_save_comments(bvid, config.cookie)