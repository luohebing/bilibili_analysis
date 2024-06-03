import sqlite3
import pandas as pd
import os
import csv
import json

csv_file_path = 'train_data.csv'
labels_map = {'angry': 0, 'sad': 0, 'fear': 0, 'happy': 2, 'neutral': 1}

# 检查文件是否存在，如果不存在则创建
if not os.path.exists(csv_file_path):
    # 定义数据
    data = {
        'Label': [],
        'Review': []
    }
    # 使用pandas DataFrame构造数据
    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, index=False)  # index=False避免写入索引列

# 读取usual_eval_labeled.txt文件
txt_file_path = 'usual_test_labeled.txt'

with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
    data_list = json.load(txt_file)  # 一次性加载整个文件为JSON列表
    for data_dict in data_list:
        label = data_dict.get('label', '')
        content = data_dict.get('content', '')

        # 根据标签写入数据
        if label in labels_map:
            label_value = labels_map[label]
            with open(csv_file_path, 'a', encoding='utf-8-sig', newline='') as train_f:
                writer = csv.writer(train_f)
                writer.writerow([label_value, content])

# 确保文件已关闭
train_f.close() if 'train_f' in locals() else None