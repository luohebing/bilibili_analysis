from sklearn.metrics import classification_report
from keras.utils import pad_sequences
import pandas as pd
import jieba
import tensorflow as tf
from sklearn.model_selection import KFold
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
import numpy as np
import re
from keras.models import load_model

# 加载停用词列表
def load_stopwords():
    with open('Text-CNN/hit_stopwords.txt', 'r', encoding='UTF-8') as f:
        stopwords = [line.strip() for line in f.readlines()]
    return stopwords

# 文本预处理函数
def preprocess_text(text, tokenizer, max_len, stopwords):
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.replace(" ", "")
    text = ' '.join(word for word in jieba.cut(text) if word not in stopwords)
    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequence, maxlen=max_len, truncating='post')
    return padded_sequence

# 定义测试文本函数
def test_text(text, model_path='Text-CNN/Text-CNN_model_fold0.h5', max_len=280):
    """
    分析输入文本的情感倾向。
    
    参数:
    - text: 输入的文本字符串。
    - model_path: 已训练模型的路径，默认为第一个fold的模型。
    - max_len: 序列的最大长度，默认为280。
    
    返回:
    - sentiment: 情感倾向标签（'Negative', 'Neutral', 'Positive'）。
    """
    # 加载停用词
    stopwords = load_stopwords()
    
    # 加载训练时使用的Tokenizer
    tokenizer = Tokenizer(num_words=25000, oov_token='<OOV>')
    tokenizer.fit_on_texts([])  # 空列表仅用于初始化Tokenizer
    
    # 预处理输入文本
    seq = preprocess_text(text, tokenizer, max_len, stopwords)
    
    # 加载模型
    model = load_model(model_path)
    
    # 预测情感倾向
    prediction = model.predict(seq)
    print(prediction)
    sentiment_index = np.argmax(prediction, axis=1)[0]
    sentiments = ['Negative', 'Neutral', 'Positive']
    sentiment = sentiments[sentiment_index]
    
    return sentiment

# 示例使用test_text函数
if __name__ == "__main__":
    sample_text = "哈哈哈哈哈哈哈哈哈哈哈哈哈"
    sentiment = test_text(sample_text)
    print(f"输入文本：'{sample_text}' 的情感倾向是：{sentiment}")