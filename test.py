from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
import jieba
import re
import numpy as np

def load_stopwords():
        """
        :return: 加载好的停用词列表
        """
        with open('Text-CNN/hit_stopwords.txt', 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            stopwords = []
            for line in lines:
                stopwords.append(line.replace('\n', ''))
        return stopwords

# 准备数据
# new_text = "我真的好伤心，要哭成泪人了，有没有小伙伴来同情一下我啊，我好难受"
new_text = "哈哈哈哈哈哈我好开心"

new_text = re.sub(r'\d+', '', new_text)
new_text = re.sub(r'[^\w\s]', '', new_text)
new_text = new_text.replace(" ", "")

# 分词并去除停用词
stop_words = load_stopwords()
new_text = [' '.join(word for word in jieba.cut(new_text) if word not in stop_words)]

# 词向量化
tokenizer = Tokenizer(num_words=25000, oov_token='<OOV>')
tokenizer.fit_on_texts(new_text)
seq = tokenizer.texts_to_sequences(new_text)
max_len = 280
padded = pad_sequences(seq, maxlen=max_len, truncating='post')

# 加载模型
model = load_model('Text-CNN/Text-CNN_model_fold9.h5')  # 这里选择其中一个折的模型进行加载

# 预测
predictions = model.predict(padded)

# 解析结果
predicted_labels = np.argmax(predictions, axis=1)

print(predicted_labels)