import sqlite3
import requests
import sys
import io
import config
import os
from PIL import Image
from io import BytesIO

# 检查另一个文件运行subprocess.run(['python', 'ranking_data.py', str(tid)], check=True)时是否提供了tid参数，验证该参数是否是由subprocess提供的
if len(sys.argv) < 2:
    print("Error: bvid argument is missing.")
    sys.exit(1)
else:
    try:
        tid = int(sys.argv[1])
    except ValueError:
        print("Error: tid argument is not an integer.")
        tid = 0
        # sys.exit(1)


# if len(sys.argv) < 2:
#     print("Error: bvid argument is missing.")
# 从命令行参数中获取tid值
# tid = sys.argv[1]

# 设置请求头
headers = config.headers

# 获取视频的 TAG 信息
def get_video_tags(aid=None, bvid=None):
    params = {}
    if aid:
        params['aid'] = aid
    elif bvid:
        params['bvid'] = bvid
    else:
        raise ValueError("Either 'aid' or 'bvid' must be provided.")

    response = requests.get('https://api.bilibili.com/x/tag/archive/tags', params=params, headers=headers)
    tag_data = response.json()['data']
    tags = [tag['tag_name'] for tag in tag_data]  # 获取每个视频的 TAG 名称
    return ','.join(tags)  # 将 TAG 名称列表转换为逗号分隔的字符串

# 设置控制台编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 连接到 SQLite 数据库
conn = sqlite3.connect('bilibili.db')

# 发送 HTTP 请求获取分区视频排行榜列表
# response = requests.get('https://api.bilibili.com/x/web-interface/ranking/v2', headers=headers)

# 发送 HTTP 请求获取分区视频排行榜列表,若tid（转化为整型）不为0，则附加url参数tid
if int(tid) != 0:
    response = requests.get('https://api.bilibili.com/x/web-interface/ranking/v2', params={
        'rid': tid,
        "dm_img_list": "[]",
        "dm_img_str": "V2ViR0wgMS",
        'dm_cover_img_str': 'SW50ZWwoUikgSEQgR3JhcGhpY3NJbnRlbA',
        }, headers=headers)
else:
    response = requests.get('https://api.bilibili.com/x/web-interface/ranking/v2', params={
        "dm_img_list": "[]",
        "dm_img_str": "V2ViR0wgMS",
        'dm_cover_img_str': 'SW50ZWwoUikgSEQgR3JhcGhpY3NJbnRlbA',
        }, headers=headers)

print("tid:", tid)
# print(response.json())
if response.json()['code'] == -352:
    print(response.json())

ranking_data = response.json()['data']['list']

# 创建表格用于保存视频排行榜数据，若tid（转化为整型）不为0，则在表名ranking后附加tid，例如ranking_1
if int(tid) != 0:
    conn.execute('''CREATE TABLE IF NOT EXISTS ranking_{} (
                    bvid TEXT PRIMARY KEY,
                    aid INTEGER,
                    videos INTEGER,
                    tid INTEGER,
                    tname TEXT,
                    copyright INTEGER,
                    pic TEXT,
                    title TEXT,
                    pubdate INTEGER,
                    ctime INTEGER,
                    desc TEXT,
                    duration INTEGER,
                    dynamic TEXT,
                    tags TEXT,
                    positive_count INTEGER,
                    neutral_count INTEGER,
                    negative_count INTEGER,
                    view INTEGER,
                    danmaku INTEGER,
                    reply INTEGER,
                    favorite INTEGER,
                    coin INTEGER,
                    share INTEGER,
                    now_rank INTEGER,
                    his_rank INTEGER,
                    like INTEGER,
                    dislike INTEGER,
                    vt INTEGER
                    )'''.format(tid))
    # 清空现有数据
    conn.execute('DELETE FROM ranking_{}'.format(tid))
else:
    conn.execute('''CREATE TABLE IF NOT EXISTS ranking (
                    bvid TEXT PRIMARY KEY,
                    aid INTEGER,
                    videos INTEGER,
                    tid INTEGER,
                    tname TEXT,
                    copyright INTEGER,
                    pic TEXT,
                    title TEXT,
                    pubdate INTEGER,
                    ctime INTEGER,
                    desc TEXT,
                    duration INTEGER,
                    dynamic TEXT,
                    tags TEXT,
                    positive_count INTEGER,
                    neutral_count INTEGER,
                    negative_count INTEGER,
                    view INTEGER,
                    danmaku INTEGER,
                    reply INTEGER,
                    favorite INTEGER,
                    coin INTEGER,
                    share INTEGER,
                    now_rank INTEGER,
                    his_rank INTEGER,
                    like INTEGER,
                    dislike INTEGER,
                    vt INTEGER
                    )''')
    # 清空现有数据
    conn.execute('DELETE FROM ranking')

# 创建表格用于保存视频排行榜数据
# conn.execute('''CREATE TABLE IF NOT EXISTS ranking (
#                 bvid TEXT PRIMARY KEY,
#                 aid INTEGER,
#                 videos INTEGER,
#                 tid INTEGER,
#                 tname TEXT,
#                 copyright INTEGER,
#                 pic TEXT,
#                 title TEXT,
#                 pubdate INTEGER,
#                 ctime INTEGER,
#                 desc TEXT,
#                 duration INTEGER,
#                 dynamic TEXT,
#                 tags TEXT,
#                 positive_count INTEGER,
#                 neutral_count INTEGER,
#                 negative_count INTEGER,
#                 view INTEGER,
#                 danmaku INTEGER,
#                 reply INTEGER,
#                 favorite INTEGER,
#                 coin INTEGER,
#                 share INTEGER,
#                 now_rank INTEGER,
#                 his_rank INTEGER,
#                 like INTEGER,
#                 dislike INTEGER,
#                 vt INTEGER
#                 )''')

# 清空现有数据
# conn.execute('DELETE FROM ranking')

# 将排行榜数据保存到数据库中
if int(tid) != 0:
    for video in ranking_data:
        stat = video['stat']
        conn.execute('''INSERT OR REPLACE INTO ranking_{} (
                        bvid, aid, videos, tid, tname, copyright, pic, title, pubdate, ctime, desc, duration, dynamic,
                        view, danmaku, reply, favorite, coin, share, now_rank, his_rank, like, dislike, vt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''.format(tid),
                        (video['bvid'], video['aid'], video['videos'], video['tid'], video['tname'], video['copyright'], video['pic'], video['title'], video['pubdate'], video['ctime'], video['desc'], video['duration'], video['dynamic'],
                        stat['view'], stat['danmaku'], stat['reply'], stat['favorite'], stat['coin'], stat['share'], stat['now_rank'], stat['his_rank'], stat['like'], stat['dislike'], stat['vt']))
else:
    for video in ranking_data:
        stat = video['stat']
        conn.execute('''INSERT OR REPLACE INTO ranking (
                        bvid, aid, videos, tid, tname, copyright, pic, title, pubdate, ctime, desc, duration, dynamic,
                        view, danmaku, reply, favorite, coin, share, now_rank, his_rank, like, dislike, vt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (video['bvid'], video['aid'], video['videos'], video['tid'], video['tname'], video['copyright'], video['pic'], video['title'], video['pubdate'], video['ctime'], video['desc'], video['duration'], video['dynamic'],
                        stat['view'], stat['danmaku'], stat['reply'], stat['favorite'], stat['coin'], stat['share'], stat['now_rank'], stat['his_rank'], stat['like'], stat['dislike'], stat['vt']))

# 获取视频排行榜列表
if int(tid) != 0:
    cur = conn.cursor()
    cur.execute("SELECT aid, bvid FROM ranking_{}".format(tid))
    videos = cur.fetchall()
else:
    cur = conn.cursor()
    cur.execute("SELECT aid, bvid FROM ranking")
    videos = cur.fetchall()

# 为每个视频添加 TAG 信息
for video in videos:
    aid, bvid = video
    tags = get_video_tags(aid=aid)  # 获取视频的 TAG 信息
    if int(tid) != 0:
        cur.execute("UPDATE ranking_{} SET tags = ? WHERE aid = ?".format(tid), (tags, aid))  # 将 TAG 信息添加到数据库中
    else:
        cur.execute("UPDATE ranking SET tags = ? WHERE aid = ?", (tags, aid))  # 将 TAG 信息添加到数据库中

# 从ranking表中读取bvid、pic项，获取pic视频封面链接并下载，将所有视频封面缩放裁剪为4:3，以jpg格式保存到bilibili-vite/public/cover/下，以bivd为文件名。
if int(tid) != 0:
    cur.execute("SELECT bvid, pic FROM ranking_{}".format(tid))
else:
    cur.execute("SELECT bvid, pic FROM ranking")
videos = cur.fetchall()
for video in videos:
    bvid, pic = video
    file_name = f"bilibili-vite/public/cover/{bvid}.jpg"
    if not os.path.exists(file_name):
        response = requests.get(pic)
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        # 裁剪图片为16:9格式
        width, height = img.size
        new_height = width * (9 / 16)
        if new_height > height:
            new_width = height * (16 / 9)
            left = (width - new_width) / 2
            img = img.crop((left, 0, left + new_width, height))
        else:
            top = (height - new_height) / 2
            img = img.crop((0, top, width, top + new_height))
        # 保存图片
        img.save(file_name)

# 提交更改并关闭连接
conn.commit()
conn.close()