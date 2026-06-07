import pandas as pd
import numpy as np
df_patient = pd.read_csv('data_clinical_patient.txt', sep='\t', comment='#')
df_sample = pd.read_csv('data_clinical_sample.txt', sep='\t', comment='#')
df_mrna = pd.read_csv('data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt', sep='\t', comment='#')
df_sample['PATIENT_ID'] = df_sample['SAMPLE_ID'].str[:12]
print("样本表与患者表主键ID已完成12位对齐")
df_mrna_clean = df_mrna.dropna(subset=['Hugo_Symbol'])
df_mrna_clean = df_mrna_clean.set_index('Hugo_Symbol')
if 'Entrez_Gene_Id' in df_mrna_clean.columns:
    df_mrna_clean = df_mrna_clean.drop(columns=['Entrez_Gene_Id'])
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
df_super.to_csv('data_multiomics_merged.csv', index=False)