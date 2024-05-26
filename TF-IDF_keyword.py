import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from difflib import SequenceMatcher
import sys

# 检查是否提供了tid参数
if len(sys.argv) < 2:
    print("Error: bvid argument is missing.")
    sys.exit(1)  # 程序退出，表示错误

# 从命令行参数中获取tid值
tid = sys.argv[1]

# 合并相似的关键词
def merge_similar_keywords(keywords_info):
    merged_keywords = {}
    for keyword, weight, bvids in keywords_info:
        matched = False
        for merged_keyword in merged_keywords:
            similarity = SequenceMatcher(None, keyword, merged_keyword).ratio()
            if similarity > 0.6:  # 如果相似度超过 0.6，则认为是相似的关键词
                merged_keywords[merged_keyword][0] += weight
                merged_keywords[merged_keyword][1].extend(bvid for bvid in bvids.split(',') if bvid not in merged_keywords[merged_keyword][1])  # 将相关视频的 bvid 合并
                matched = True
                break
        if not matched:
            merged_keywords[keyword] = [weight, bvids.split(',')]
    return merged_keywords

# 连接到数据库
conn = sqlite3.connect('bilibili.db')

# 查询数据库获取视频信息
cur = conn.cursor()
if int(tid) != 0:
    cur.execute("SELECT title, tags, bvid FROM ranking_{}".format(tid))
else:
    cur.execute("SELECT title, tags, bvid FROM ranking")
videos = cur.fetchall()

# 将标题和标签组合成文档列表
documents = []
for title, tags, bvid in videos:
    document = title + ' ' + tags  # 将标题和标签合并为一个文档
    documents.append(document)  # 只保存文档，不保存bvid

# 使用 TF-IDF 算法进行关键词提取
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
feature_names = tfidf_vectorizer.get_feature_names_out()

# 计算全局关键词权重并保存相关视频的 bvid
keyword_weights = {}
keyword_bvids = {}
for i, keyword in enumerate(feature_names):
    total_weight = tfidf_matrix[:, i].sum()  # 获取关键词在所有文档中的 TF-IDF 总和
    keyword_weights[keyword] = total_weight
    keyword_bvids[keyword] = []

# 获取排行榜中视频的数量
num_videos = len(videos)

# 按照视频在排行榜中的位置进行加权
for i, document in enumerate(documents):
    tfidf_vector = tfidf_vectorizer.transform([document])  # 计算该视频的 TF-IDF 向量
    feature_indices = tfidf_vector.nonzero()[1]  # 获取非零元素的列索引（即关键词的索引）
    for idx in feature_indices:
        keyword = feature_names[idx]
        weight = tfidf_vector[0, idx] * (1 - i / num_videos)  # 根据视频在排行榜中的位置进行加权
        keyword_weights[keyword] += weight.item()  # 将稀疏矩阵元素转换为标量值，并进行加法运算
        if videos[i][2] not in keyword_bvids[keyword]:
            keyword_bvids[keyword].append(videos[i][2])

# 创建新表用于保存关键词及其权重和相关视频的 bvid
conn.execute('''CREATE TABLE IF NOT EXISTS keywords (
                keyword TEXT PRIMARY KEY,
                weight REAL,
                bvids TEXT,
                positive_count INTEGER,
                neutral_count INTEGER,
                negative_count INTEGER
                )''')
# 清空 keywords 表
conn.execute("DELETE FROM keywords")

# 将关键词及其权重和相关视频的 bvid 保存到数据库中
sorted_keywords = sorted(keyword_weights.items(), key=lambda x: x[1], reverse=True)
for keyword, weight in sorted_keywords:
    bvids = ','.join(keyword_bvids[keyword])
    conn.execute("INSERT INTO keywords (keyword, weight, bvids) VALUES (?, ?, ?)", (keyword, weight, bvids))

# 过滤分区标签
# 获取ranking表中的所有不重复的tname值
cur.execute("SELECT DISTINCT tname FROM ranking" if int(tid) == 0 else "SELECT DISTINCT tname FROM ranking_{}".format(tid))
tname_values = [row[0] for row in cur.fetchall()]

# 获取关键词表中的所有关键词
cur.execute("SELECT keyword FROM keywords")
keywords = [row[0] for row in cur.fetchall()]

# 创建相似度阈值，用于确定相似性
SIMILARITY_THRESHOLD = 0.5

# 对于每个关键词，检查是否与任何tname值相同或相似
for keyword in keywords:
    for tname in tname_values:
        similarity_ratio = SequenceMatcher(None, keyword, tname).ratio()
        if similarity_ratio > SIMILARITY_THRESHOLD:
            # 如果关键词与tname相似，则从关键词表中删除该关键词
            conn.execute("DELETE FROM keywords WHERE keyword=?", (keyword,))
            break  # 找到相似项后，不再继续比较其他tname值

# 合并相似的关键词
cur.execute("SELECT keyword, weight, bvids FROM keywords")
keywords_info = cur.fetchall()
merged_keywords = merge_similar_keywords(keywords_info)
# 排序并获取权重前100个关键词
sorted_keywords = sorted(merged_keywords.items(), key=lambda x: x[1][0], reverse=True)[:100]
# 清空 keywords 表
conn.execute("DELETE FROM keywords")
# 将更新后的关键词信息保存到数据库中
for keyword, (weight, bvids) in sorted_keywords:
    bvids_str = ','.join(bvids)
    conn.execute("INSERT INTO keywords (keyword, weight, bvids) VALUES (?, ?, ?)", (keyword, weight, bvids_str))

# 提交更改并关闭连接
conn.commit()
conn.close()
