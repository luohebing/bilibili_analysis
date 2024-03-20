import pandas as pd

# 读取CSV文件
df = pd.read_csv('Text-CNN/train.csv')

# 用特定值填充NaN值，例如中性情感对应的标签1
df['label'].fillna(1, inplace=True)


# 保存修改后的数据到同一文件
df.to_csv('Text-CNN/train.csv', index=False)