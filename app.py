from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, send
import sqlite3
import tools
import os
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)  # 这行代码会启用 CORS，允许跨域请求
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")  # 添加 CORS 设置


@app.errorhandler(500)
def handle_500(error):
    return jsonify({"error": str(error)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"key": "value"}  # 这里可以是你的实际数据
    return jsonify(data)


@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    tid = request.args.get('tid')
    tools.get_keywords(tid)
    tools.generate_wordcloud_from_db()
    conn = sqlite3.connect('bilibili.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM keywords")
    data = cursor.fetchall()
    conn.close()

    # 尝试使用不同的编码来解码字节对象
    data = [list(row) for row in data]  # Convert tuples to lists
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            if isinstance(item, bytes):
                try:
                    data[i][j] = item.decode("utf-8")
                except UnicodeDecodeError:
                    data[i][j] = item.decode("ISO-8859-1")

    return jsonify(data)

@app.route('/api/videos', methods=['GET'])
def get_videos():
    keyword = request.args.get('keyword')
    tid = request.args.get('tid')
    conn = sqlite3.connect('bilibili.db')
    cursor = conn.cursor()

    # 从 keywords 表中获取与 keyword 相关的 bvids
    cursor.execute("SELECT bvids FROM keywords WHERE keyword=?", (keyword,))
    bvids = cursor.fetchone()
    if bvids is None:
        return jsonify([])

    # 将 bvids 字符串分割成列表
    bvids = bvids[0].split(',')

    # 从 ranking 表中获取与 bvids 相关的视频
    videos = []
    for bvid in bvids:
        if int(tid) == 0:
            cursor.execute("SELECT * FROM ranking WHERE bvid=?", (bvid,))
        else:
            cursor.execute(f"SELECT * FROM ranking_{tid} WHERE bvid=?", (bvid,))
        video = cursor.fetchone()
        if video is not None:
            videos.append(video)
            # 下载封面图片
            pic_url = video[6]
            file_name = f"bilibili-vite/public/cover/{bvid}.jpg"
            if not os.path.exists(file_name):
                response = requests.get(pic_url)
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
            # file_extension = os.path.splitext(pic_url)[1]  # 获取文件扩展名
            # file_name = f"Cache/{bvid}{file_extension}"
            # file_name = f"bilibili-vite/public/cover/{bvid}.jpg"
            # with open(file_name, 'wb') as f:
            #     f.write(response.content)

    conn.close()

    # 尝试使用不同的编码来解码字节对象
    videos = [list(video) for video in videos]  # Convert tuples to lists
    for i, video in enumerate(videos):
        for j, item in enumerate(video):
            if isinstance(item, bytes):
                try:
                    videos[i][j] = item.decode("utf-8")
                except UnicodeDecodeError:
                    videos[i][j] = item.decode("ISO-8859-1")

    return jsonify(videos)

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    flag = request.args.get('flag')
    value = request.args.get('value')

    # 运行情感分析
    tools.run_sentiment_analysis(flag, value)

    if flag == 'keyword':
        # 连接数据库
        conn = sqlite3.connect('bilibili.db')
        cursor = conn.cursor()

        # 查询数据库
        cursor.execute("SELECT positive_count, neutral_count, negative_count FROM keywords WHERE keyword=?", (value,))
        data = cursor.fetchone()

        # 关闭数据库连接
        conn.close()

        if data is None:
            return jsonify([])

        return jsonify(list(data))
    
    if flag == 'bvid':
        # 连接数据库
        conn = sqlite3.connect('bilibili.db')
        cursor = conn.cursor()

        # 查询数据库
        cursor.execute("SELECT positive_count, neutral_count, negative_count FROM specific_video WHERE bvid=?", (value,))
        data = cursor.fetchone()

        # 关闭数据库连接
        conn.close()

        if data is None:
            return jsonify([])

        return jsonify(list(data))

    return jsonify({"message": "Invalid flag"})

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    tid = request.args.get('tid')
    if tid is None:
        tid = 0
    # tools.get_ranking_data(tid)
    conn = sqlite3.connect('bilibili.db')
    cursor = conn.cursor()
    if int(tid) == 0:
        cursor.execute("SELECT * FROM ranking")
    else:
        cursor.execute(f"SELECT * FROM ranking_{tid}")
    data = cursor.fetchall()
    conn.close()

    # 尝试使用不同的编码来解码字节对象
    data = [list(row) for row in data]  # Convert tuples to lists
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            if isinstance(item, bytes):
                try:
                    data[i][j] = item.decode("utf-8")
                except UnicodeDecodeError:
                    data[i][j] = item.decode("ISO-8859-1")

    return jsonify(data)

    # tools.get_ranking_data()
    # conn = sqlite3.connect('bilibili.db')
    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM ranking")
    # data = cursor.fetchall()
    # conn.close()

    # # 尝试使用不同的编码来解码字节对象
    # data = [list(row) for row in data]  # Convert tuples to lists
    # for i, row in enumerate(data):
    #     for j, item in enumerate(row):
    #         if isinstance(item, bytes):
    #             try:
    #                 data[i][j] = item.decode("utf-8")
    #             except UnicodeDecodeError:
    #                 data[i][j] = item.decode("ISO-8859-1")

    # return jsonify(data)

@app.route('/api/updateranking', methods=['GET'])
def update_ranking():
    for tid in [0, 1, 3, 129, 4, 36, 188, 234, 223, 160, 211, 217, 119, 155, 5, 181, 177, 23, 11]:
    # for tid in [11]:
        tools.get_ranking_data(tid)
    return jsonify({"message": "Ranking data updated successfully"})
    

@app.route('/api/specific_video', methods=['GET'])
def get_specific_video():
    bvid = request.args.get('bvid')
    conn = sqlite3.connect('bilibili.db')
    cursor = conn.cursor()

    ranking_video = None

    # 遍历数据库中所有以ranking开头的表，如ranking，rankingabc等，若匹配bvid对应的项，中断遍历，将该项赋值给ranking_video
    # 查询数据库中的所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    # 遍历结果，查找以 "ranking" 为前缀的表名
    for table in cursor.fetchall():
        table_name = table[0]
        if table_name.startswith("ranking"):
            # print("Found table:", table_name)
            cursor.execute(f"SELECT * FROM {table_name} WHERE bvid=?", (bvid,))
            ranking_video = cursor.fetchone()
            if ranking_video:
                break
        
    # Check if bvid exists in ranking table
    # cursor.execute("SELECT * FROM ranking WHERE bvid=?", (bvid,))
    # ranking_video = cursor.fetchone()
    
    # Check if bvid exists in specific_video table
    cursor.execute("SELECT * FROM specific_video WHERE bvid=?", (bvid,))
    specific_video = cursor.fetchone()

    

    if ranking_video:
        video = list(ranking_video)
    elif specific_video:
        video = list(specific_video)
    else:
        tools.get_video(bvid)
        cursor.execute("SELECT * FROM specific_video WHERE bvid=?", (bvid,))
        video = list(cursor.fetchone())

    conn.close()

    # cid = tools.get_cid(bvid)  # 获取cid
    # video.append(cid)  # 将cid添加到video数组末端

    return jsonify(video)

@app.route('/api/emotion/cache/size', methods=['GET'])
def get_emotion_cache_size():
    conn = sqlite3.connect('bilibili.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(length(sql))/1024 FROM sqlite_master WHERE type='table' AND name LIKE 'bvid_%'")
    total_size_kb = cursor.fetchone()[0]
    conn.close()

    # 转换大小为适当的单位
    if total_size_kb is not None:
        if total_size_kb < 1024:  # 小于1MB
            size_str = f"{total_size_kb:.2f} KB"
        elif total_size_kb < 1024 * 1024:  # 小于1GB
            size_str = f"{total_size_kb / 1024:.2f} MB"
        else:  # 大于等于1GB
            size_str = f"{total_size_kb / (1024 * 1024):.2f} GB"
    else:
        size_str = "0.00KB"

    return jsonify(size_str)

@app.route('/api/emotion/cache/clear', methods=['GET'])
def clear_emotion_cache():
    tools.clear_cache_tables('bilibili.db')
    return get_emotion_cache_size()

@app.route('/api/video/cache/size', methods=['GET'])
def get_video_cache_size():
    path = 'bilibili-vite/public/cover'
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
    total_size_kb = total_size / 1024
    # 转换大小为适当的单位
    if total_size_kb < 1024:  # 小于1MB
        size_str = f"{total_size_kb:.2f} KB"
    elif total_size_kb < 1024 * 1024:  # 小于1GB
        size_str = f"{total_size_kb / 1024:.2f} MB"
    else:  # 大于等于1GB
        size_str = f"{total_size_kb / (1024 * 1024):.2f} GB"
    return jsonify(size_str)

@app.route('/api/video/cache/clear', methods=['GET'])
def clear_video_cache():
    tools.clear_image_cache()
    return get_video_cache_size()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)