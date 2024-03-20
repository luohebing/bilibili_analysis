import subprocess
import os
import sqlite3
from config import database_name
import config
from flask import Flask, render_template, request, g
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests

#更新ranking排行榜
def get_ranking_data():
    try:
        subprocess.run(['python', 'ranking_data.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Error: 'ranking_data.py' not found in the current directory.")

#更新keyword关键词
def get_keywords():
    try:
        subprocess.run(['python', 'TF-IDF_keyword.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Error: 'TF-IDF_keyword.py' not found in the current directory.")

#获取指定视频信息到specific_video
def get_video(bvid):
    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 构建get_video.py的路径
    script_path = os.path.join(current_directory, 'get_video.py')
    # 检查脚本文件是否存在
    if not os.path.exists(script_path):
        print("Error: get_video.py not found in the current directory.")
        return
    
    try:
        # 使用subprocess运行脚本，并传递新的bvid参数
        subprocess.run(['python', script_path, bvid])
    except Exception as e:
        print(f"Error occurred while running get_video.py: {e}")

# 调用函数来执行get_video.py脚本并传递新的bvid参数
# new_bvid_value = "BV1mm411Q7mC"
# get_video(new_bvid_value)
        
# 对关键词或指定视频进行情感分析
def run_sentiment_analysis(flag, value):
    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # 构建sentiment_analysis.py的路径
    script_path = os.path.join(current_directory, 'sentiment_analysis.py')
    
    # 检查脚本文件是否存在
    if not os.path.exists(script_path):
        print("Error: sentiment_analysis.py not found in the current directory.")
        return
    
    try:
        # 使用subprocess运行脚本，并传入参数
        subprocess.run(['python', script_path, flag, value])
    except Exception as e:
        print(f"Error occurred while running sentiment_analysis.py: {e}")

# 调用函数来执行sentiment_analysis.py脚本，并传入flag和相应的值
# flag = "keyword"  # 或者 "bvid" BV1mm411Q7mC
# value = "海底捞"
# run_sentiment_analysis(flag, value)

#清空弹幕与评论缓存
def clear_cache_tables(database_name):
    # 连接到数据库
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    try:
        # 获取数据库中所有表的名称
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # 遍历所有表
        for table in tables:
            table_name = table[0]
            # 判断表名是否符合要求
            if table_name.startswith("bvid_") and ("_danmaku" in table_name or "_reply" in table_name):
                # 清除表
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                print(f"Table '{table_name}' dropped.")

        conn.commit()
        print("Cache tables cleared successfully.")

    except Exception as e:
        print("Error:", e)
        conn.rollback()

    finally:
        # 关闭连接
        cursor.close()
        conn.close()

# 示例调用函数
# clear_cache_tables("bilibili.db")
        
# 清除指定视频弹幕与评论缓存
def clear_tables_with_string(database_name, target_string):
    # 连接到数据库
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    try:
        # 获取数据库中所有表的名称
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # 遍历所有表
        for table in tables:
            table_name = table[0]
            # 判断表名是否包含指定字符串
            if target_string in table_name:
                # 清除表
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                print(f"Table '{table_name}' dropped.")

        conn.commit()
        print(f"Tables containing '{target_string}' cleared successfully.")

    except Exception as e:
        print("Error:", e)
        conn.rollback()

    finally:
        # 关闭连接
        cursor.close()
        conn.close()

# 示例调用函数
# clear_tables_with_string("bilibili.db", "BV1Zp421R7tF")
        
# 词云文件生成
def generate_wordcloud_from_db():
    # 连接到数据库
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # 执行查询以获取关键词和权重
    cursor.execute("SELECT keyword, weight FROM keywords")
    data = cursor.fetchall()

    # 创建一个字典，其中关键词是键，权重是值
    word_weights = {row[0]: row[1] for row in data}

    # 使用 WordCloud 类生成词云图
    wordcloud = WordCloud(background_color='rgba(255, 255, 255, 0)', mode='RGBA', font_path='simsun.ttc', width=1000, height=550).generate_from_frequencies(word_weights)
    

    # 保存词云图为图像文件
    wordcloud.to_file('bilibili-vite/public/icon/wordcloud.png')

    # 关闭连接
    cursor.close()
    conn.close()

# 清空图片缓存：删除bilibili-vite/public/cover/下所有BV开头的文件
def clear_image_cache():
    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 构建bilibili-vite/public/cover的路径
    public_path = os.path.join(current_directory, 'bilibili-vite/public/cover')
    # 检查路径是否存在
    if not os.path.exists(public_path):
        print("Error: 'bilibili-vite/public' not found in the current directory.")
        return
    
    try:
        # 获取bilibili-vite/public/cover/下所有文件
        files = os.listdir(public_path)
        # 遍历所有文件
        for file in files:
            # 判断文件名是否以BV开头
            if file.startswith("BV"):
                # 删除文件
                os.remove(os.path.join(public_path, file))
                print(f"File '{file}' deleted.")
        print("Image cache cleared successfully.")
    except Exception as e:
        print(f"Error occurred while clearing image cache: {e}")

#获取cid
def get_cid(bvid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
        'Cookie': config.cookie
    }
    cid_url = f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp'
    cid_response = requests.get(cid_url, headers=headers)
    cid_data = cid_response.json()
    cid = cid_data['data'][0]['cid']
    return cid