import pandas as pd
df_patient = pd.read_csv('data_clinical_patient.txt', sep='\t', comment='#')
print(f"患者加载成功,尺寸为: {df_patient.shape}, 主键列示例: {df_patient['PATIENT_ID'].head(3).tolist()}")
df_sample = pd.read_csv('data_clinical_sample.txt', sep='\t', comment='#')
print(f"样本加载成功,尺寸为: {df_sample.shape}, 是否包含肿瘤级别分级列: { 'GRADE' in df_sample.columns }")
df_mrna = pd.read_csv('data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt', sep='\t', comment='#')
print(f" mRNA 表达谱加载成功,尺寸为: {df_mrna.shape},包含的基因数量：{df_mrna.shape[0]}")
