import sqlite3
import requests
import xml.etree.ElementTree as ET
import config


def fetch_and_save_danmaku(bvid):
    # 设置请求头
    headers = config.headers
    # 获取视频cid
    cid_url = f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp'
    cid_response = requests.get(cid_url, headers=headers)
    cid_data = cid_response.json()
    cid = cid_data['data'][0]['cid']
    
    # 发送请求获取弹幕信息
    danmaku_url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}'
    danmaku_response = requests.get(danmaku_url, headers=headers)
    danmaku_xml = danmaku_response.content
    
    # 解析XML格式的弹幕信息
    root = ET.fromstring(danmaku_xml)
    
    # 连接到数据库
    conn = sqlite3.connect('bilibili.db')
    cur = conn.cursor()
    
    # 创建表格
    table_name = f'bvid_{bvid}_danmaku'
    cur.execute(f'DROP TABLE IF EXISTS {table_name}')  # 清空表格
    cur.execute(f'CREATE TABLE {table_name} (time REAL, type INTEGER, fontsize INTEGER, color INTEGER, timestamp INTEGER, sender_hash TEXT, dmid INTEGER, block_level INTEGER, content TEXT)')
    
    # 提交更改
    conn.commit()
    
    # 提取弹幕并保存到数据库
    for d in root.findall('d'):
        p = d.attrib['p'].split(',')
        time = float(p[0])
        type = int(p[1])
        fontsize = int(p[2])
        color = int(p[3])
        timestamp = int(p[4])
        sender_hash = p[5]
        dmid = p[6]  # 将 DMID 保留为字符串形式
        block_level = int(p[7])
        content = d.text
        cur.execute(f"INSERT INTO {table_name} (time, type, fontsize, color, timestamp, sender_hash, dmid, block_level, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (time, type, fontsize, color, timestamp, sender_hash, dmid, block_level, content))
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()

# 示例使用
bvid = 'BV1kU421d7YH'  # 视频的 bvid
fetch_and_save_danmaku(bvid)
