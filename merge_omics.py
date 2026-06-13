import pandas as pd
import numpy as np
from pathlib import Path

patient_path = Path('data/processed/patient_cleaned.csv')
expression_path = Path('data/processed/expression_cleaned.csv')
output_path = Path('data/processed/data_multiomics_merged.csv')
if not patient_path.is_file():
    raise FileNotFoundError(
        "Cleaned patient table not found. Run: python src/data/clean_patient.py"
    )
if not expression_path.is_file():
    raise FileNotFoundError(
        "Cleaned expression matrix not found. Run: python src/data/clean_expression.py"
    )

df_patient = pd.read_csv(patient_path)
df_sample = pd.read_csv('data_clinical_sample.txt', sep='\t', comment='#')
df_mrna = pd.read_csv(expression_path)
print(f"patient 表 shape: {df_patient.shape}")
print(f"sample 表 shape: {df_sample.shape}")
print(f"expression 表 shape: {df_mrna.shape}")

if 'PATIENT_ID' not in df_patient.columns:
    raise KeyError("清洗后的 patient 表缺少 PATIENT_ID。")
if df_patient['PATIENT_ID'].isna().any() or df_patient['PATIENT_ID'].duplicated().any():
    raise ValueError("清洗后的 patient 表存在缺失或重复 PATIENT_ID，停止合并。")
if 'SAMPLE_ID' not in df_sample.columns:
    raise KeyError("sample 表缺少 SAMPLE_ID。")
if 'Hugo_Symbol' not in df_mrna.columns:
    raise KeyError("expression 表缺少 Hugo_Symbol。")
if df_mrna['Hugo_Symbol'].isna().any() or df_mrna['Hugo_Symbol'].duplicated().any():
    raise ValueError("清洗后的 expression 表存在缺失或重复 Hugo_Symbol，停止合并。")

df_sample['PATIENT_ID'] = df_sample['SAMPLE_ID'].str[:12]
print("样本表与患者表主键ID已完成12位对齐")
df_mrna_clean = df_mrna.set_index('Hugo_Symbol')
df_mrna_transposed = df_mrna_clean.T
df_mrna_transposed['PATIENT_ID'] = df_mrna_transposed.index.astype(str).str[:12]
df_mrna_transposed = df_mrna_transposed.reset_index(drop=True)
print(f"mRNA表达谱已完成转置，最新维度:样本{df_mrna_transposed.shape[0]} x 基因特征{df_mrna_transposed.shape[1]}")
df_clinical = pd.merge(df_sample, df_patient, on='PATIENT_ID', how='inner')
print(f"临床数据与样本数据已合并完成,样本数: {df_clinical.shape[0]},")
df_super = pd.merge(df_clinical, df_mrna_transposed, on='PATIENT_ID', how='inner')
print(f"最终整合数据集已完成,维度: {df_super.shape[0]}患者 x {df_super.shape[1]}特征")
required_col = ['PATIENT_ID', 'AGE','SEX','OS_STATUS','OS_MONTHS','GRADE']
for col in required_col:
    if col in df_super.columns:
        print(f"关键列 {col} 在最终数据集中存在")
if 'IDH1' in df_super.columns and 'TP53' in df_super.columns:
    print("基因表达数据已成功整合到最终数据集中")
output_path.parent.mkdir(parents=True, exist_ok=True)
df_super.to_csv(output_path, index=False)
print(f"安全合并结果已保存到: {output_path}")
