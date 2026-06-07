import pandas as pd
try:
    df = pd.read_csv("data_clinical_patient.txt", sep="\t", comment="#")
    print("数据读取成功！\n")
except FileNotFoundError:
    print(f"数据文件未找到，请检查文件路径：\n")
    df = None
if df is not None:
    print("---表格前五行数据---")
    print(df.head())
    print("\n---表格行列尺寸---")
    print(df.shape)
    print("\n---表格信息---")
    print(df.info())
    print("\n---提取表格前10行的前5列数据---")
    sub_matrix = df.iloc[0:10, 0:5]
    print(sub_matrix)
null_counts = df.isnull().sum()
print("各临床指标缺失值统计：")
print(null_counts[null_counts > 0]) 
df.dropna(subset=['OS_MONTHS', 'OS_STATUS'], inplace=True)
print(f"删除缺失生存标签的样本后，剩余的样本量为：{df.shape[0]}")
median_age = df['AGE'].median()
df['AGE'].fillna(median_age, inplace=True)
df['SEX'].fillna("Unknown", inplace=True)
high_risk_group = df[(df['AGE'] > 50) & (df['OS_STATUS'] == '1:DECEASED')]
print(f"筛选出高危（高龄且已死亡）样本数量为：{high_risk_group.shape[0]}")
df.to_csv("data_clinical_cleaned.csv", index=False)
print("清洗后的数据已保存到 data_clinical_cleaned.csv 文件中。")