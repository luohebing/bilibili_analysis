import sqlite3
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
import jieba
import re
import numpy as np
import get_reply
import get_danmaku
import config
import sys

# 检查是否提供了正确数量的参数
if len(sys.argv) != 3:
    print("Usage: python sentiment_analysis.py <flag> <value>")
# 获取传入的参数
flag = sys.argv[1]
value = sys.argv[2]

# 定义关键字
# keyword = 'BV1bm411975K'
# bvid = 'BV1iF4m177S8'

# 加载停用词
def load_stopwords():
    with open('Text-CNN/hit_stopwords.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        stopwords = [line.replace('\n', '') for line in lines]
    return stopwords

# 加载模型
def load_sentiment_model(model_path):
    model = load_model(model_path)
    return model

# 预处理文本
def preprocess_text(text, stop_words):
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.replace(" ", "")
    return ' '.join(word for word in jieba.cut(text) if word not in stop_words)

# 对文本进行情感分析
def analyze_sentiment(texts, model, tokenizer, max_len):
    seq = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(seq, maxlen=max_len, truncating='post')
    predictions = model.predict(padded)
    return predictions

# 分支选择 关键词/视频
def get_bvids(flag, value):
    if flag == "keyword":
        # 查询匹配关键字的 bvids
        cursor.execute("SELECT bvids FROM keywords WHERE keyword=?", (value,))
        result = cursor.fetchone()
        if result:
            bvids_str = result[0]  # 获取 bvids 字符串
            bvids = bvids_str.split(',')  # 拆分为 bvid 列表
        else:
            print("未找到与关键字匹配的 bvids")
            conn.close()
            exit()
    elif flag == "bvid":
        bvids_str = value  # 获取 bvids 字符串
        bvids = bvids_str.split(',')  # 拆分为 bvid 列表
    else:
        print("未提供有效的参数")
    return bvids

# 连接数据库
conn = sqlite3.connect('bilibili.db')
cursor = conn.cursor()

# 查询匹配关键字的 bvids
bvids=get_bvids(flag,value)
# bvids=get_bvids(keyword=keyword)

# 初始化存储所有文本的列表
all_texts = []

# 读取每个 bvid 对应的弹幕文本和评论文本
for bvid in bvids:
    get_danmaku.fetch_and_save_danmaku(bvid,config.cookie)
    get_reply.fetch_and_save_comments(bvid,config.cookie)
    # 读取弹幕文本
    cursor.execute("SELECT content FROM bvid_{}_danmaku".format(bvid))
    danmaku_texts = [row[0] for row in cursor.fetchall()]

    # 读取评论文本
    cursor.execute("SELECT comment FROM bvid_{}_reply".format(bvid))
    reply_texts = [row[0] for row in cursor.fetchall()]

    # 合并弹幕与评论文本
    all_texts.extend(danmaku_texts + reply_texts)

if all_texts is None:
    print("无弹幕与评论信息！")
    conn.close()
    exit()

# 加载停用词表
stop_words = load_stopwords()

# 预处理文本
preprocessed_texts = [preprocess_text(text, stop_words) for text in all_texts]

# print(preprocessed_texts)

# 加载情感分析模型
model = load_sentiment_model('Text-CNN/Text-CNN_model_fold9.h5')

# 加载 Tokenizer
tokenizer = Tokenizer(num_words=25000, oov_token='<OOV>')
tokenizer.fit_on_texts(preprocessed_texts)
max_len = 280

# print(preprocessed_texts)

# 对文本进行情感分析
predictions = analyze_sentiment(preprocessed_texts, model, tokenizer, max_len)

# 统计正面和负面情感的数量
positive_count = np.sum(predictions[:, 2] > 0.5)
neutral_count = np.sum(predictions[:, 1] > 0.5)
negative_count = np.sum(predictions[:, 0] > 0.5)

# 保存到数据库
if flag == "keyword":
    cursor.execute("SELECT * FROM keywords WHERE keyword = ?", (value,))
    result = cursor.fetchone()
    if result:
        keyword = result[0]
        cursor.execute("UPDATE keywords SET positive_count = ?, neutral_count = ?, negative_count = ? WHERE keyword = ?", (int(positive_count), int(neutral_count), int(negative_count), keyword))
        conn.commit()
    else:
        print("No matching record found for value:", value)
elif flag == "bvid":
    cursor.execute("SELECT * FROM specific_video WHERE bvid = ?", (value,))
    result = cursor.fetchone()
    if result:
        bvid = result[0]
        cursor.execute("UPDATE specific_video SET positive_count = ?, neutral_count = ?, negative_count = ? WHERE bvid = ?", (int(positive_count), int(neutral_count), int(negative_count), bvid))
        conn.commit()
    else:
        print("No matching record found for value:", value)
else:
    print("未提供有效的参数")

# 计算百分比
total_count = len(predictions)
positive_percentage = positive_count / total_count * 100
neutral_percentage = neutral_count / total_count * 100
negative_percentage = negative_count / total_count * 100

print("正面情感占比：{}%".format(positive_percentage))
print("中性情感占比：{}%".format(neutral_percentage))
print("负面情感占比：{}%".format(negative_percentage))

# 关闭数据库连接
conn.close()