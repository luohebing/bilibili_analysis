import requests
import sqlite3
import tools
import config
import sys



#目标视频
# 检查是否提供了bvid参数
if len(sys.argv) < 2:
    print("Error: bvid argument is missing.")
# 从命令行参数中获取bvid值
bvid = sys.argv[1]

print("bvid: " + bvid)

# 设置请求头
headers = config.headers

# 获取单个视频的详细信息
def get_specific_video_info(bvid):
    params = {}
    params['bvid'] = bvid
    print("bvid: " + bvid)

    response = requests.get('https://api.bilibili.com/x/web-interface/view', params=params, headers=headers)
    # video_data = response.json()
    # print(video_data)
    video_data = response.json()['data']
    #print(video_data)
    return video_data


# 连接到数据库
conn = sqlite3.connect('bilibili.db')

# 创建 specific_video 表格
conn.execute('''CREATE TABLE IF NOT EXISTS specific_video (
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

# 获取指定视频的详细信息
video = get_specific_video_info(bvid) 

# 将视频详细信息保存到 specific_video 表中
conn.execute('''INSERT OR REPLACE INTO specific_video (
                bvid, aid, videos, tid, tname, copyright, pic, title, pubdate, ctime, desc, duration, dynamic,
                view, danmaku, reply, favorite, coin, share, now_rank, his_rank, like, dislike, vt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (video['bvid'], video['aid'], video['videos'], video['tid'], video['tname'], video['copyright'], video['pic'], video['title'], video['pubdate'], video['ctime'], video['desc'], video['duration'], video['dynamic'],
                video['stat']['view'], video['stat']['danmaku'], video['stat']['reply'], video['stat']['favorite'], video['stat']['coin'], video['stat']['share'], video['stat']['now_rank'], video['stat']['his_rank'], video['stat']['like'], video['stat']['dislike'], video['stat']['vt']))

#添加 TAG 信息
tags = tools.get_video_tags(aid=video['aid'])  # 获取视频的 TAG 信息
conn.execute("UPDATE specific_video SET tags = ? WHERE aid = ?", (tags, video['aid']))  # 将 TAG 信息添加到数据库中

# 插入新项到 keywords 表中，缺省 weight
# bvid = video['bvid']  # 你的 bvid 值
# conn.execute("INSERT INTO keywords (keyword, bvids) VALUES (?, ?)", (bvid, bvid))

# 提交更改并关闭连接
conn.commit()
conn.close()