import pandas as pd

df_boxnum = pd.read_csv('data/LA_givendata_sample_4.csv')

# Sku code
# df_boxnum group by "Sku Code" count
df_boxnum_grouped = df_boxnum.groupby("Sku Code").count()
pre_count_df = df_boxnum_grouped.rename(columns={"오더번호": "개수: 오더번호"}).reset_index()
print(pre_count_df.head())
count_df = pre_count_df[["Sku Code", "개수: 오더번호"]]
count_df = count_df.sort_values(by="개수: 오더번호", ascending=False)
count_df.to_csv('data/LA_givendata_sample_5.csv', index=False)

# Sku code
# df_boxnum group by "Sku Code" count
df_boxnum_pcs = df_boxnum.groupby("Sku Code").sum()
pre_count_pcs_df = df_boxnum_pcs.rename(columns={"pcs출하": "합계: pcs출하"}).reset_index()
print(pre_count_pcs_df.head())
count_pcs_df = pre_count_pcs_df[["Sku Code", "합계: pcs출하"]]
count_pcs_df = count_pcs_df.sort_values(by="합계: pcs출하", ascending=False)
#merge the two dataframes with the same "Sku Code"
f_count_df = pd.merge(count_df, count_pcs_df, on="Sku Code")
f_count_df.to_csv('data/LA_givendata_sample_6.csv', index=False)