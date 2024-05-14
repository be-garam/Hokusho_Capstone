import pandas as pd
import numpy as np
import random

# seed = 42 #should be inputed
# random.seed(seed)

df_boxnum = pd.read_csv('data/LA_givendata_sample_4.csv')

# df_boxnum group by "Sku Code" count
df_boxnum_grouped = df_boxnum.groupby("Sku Code").count()
pre_count_df = df_boxnum_grouped.rename(columns={"오더번호": "개수: 오더번호"}).reset_index()
# print(pre_count_df.head())
count_df = pre_count_df[["Sku Code", "개수: 오더번호"]]
count_df = count_df.sort_values(by="개수: 오더번호", ascending=False)
count_df.to_csv('data/LA_givendata_sample_5.csv', index=False)

# df_boxnum group by "Sku Code" count
df_boxnum_pcs = df_boxnum.groupby("Sku Code").sum()
pre_count_pcs_df = df_boxnum_pcs.rename(columns={"pcs출하": "합계: pcs출하"}).reset_index()
# print(pre_count_pcs_df.head())
count_pcs_df = pre_count_pcs_df[["Sku Code", "합계: pcs출하"]]
count_pcs_df = count_pcs_df.sort_values(by="합계: pcs출하", ascending=False)
#merge the two dataframes with the same "Sku Code"
f_count_df = pd.merge(count_df, count_pcs_df, on="Sku Code")
f_count_df.to_csv('data/LA_givendata_sample_6.csv', index=False)

# 생각한 알고리즘
# 1. "합계: pcs출하"를 기준으로 내림차순 정렬
# 2. "합계: pcs출하"가 standard_pcs보다 크면 zone_list에 "PLT" 추가
# 3. 남은 "합계: pcs출하"를 반으로 쪼개고, 작은 부분은 reverse로 정렬
# 4. random하게 숫자를 뽑아 큰 리스트와 작은 리스트에서 해당하는 index를 뽑아 zone_list에 추가
# 5. 총합이 standard_error 이하가 되도록 더하다가, 큰 리스트에서 뽑은 값 이후 작은 리스트에서 뽑은 값을 더했을 때를 기준으로 분기
# 5.1. 큰 리스트에서 뽑은 값까지 더했을 때, STANDARD_ERROR만큼 뺀값보다 크면 멈추기
# 5.2. 작은 리스트에서 뽑은 값 중 

# 2차 생각 알고리즘 
# 3까지 동일
# 4. RANDOM하게 뽑아, zone에 넣는다.
# 5. 큰리스트, 작은 리스트에서 번갈아 뽑으며 큰리스트에서 나온 값은 가장 작은 총합을 가진 zone에 할당, 작은리스트에서 나온 값은 가장 큰 총합을 가진 zone에 할당

# 3차 알고리즘
# 1. 그냥 간단하게 sorting 되어 있으니 min한 곳에 넣어 전체 업무 밸런스를 맞춘다.


# Setting Metadata
zone_num = 10 #should be inputed
total_psc = sum(f_count_df["합계: pcs출하"])
total_order = sum(f_count_df["개수: 오더번호"])

standard_num = 31.5 #should be inputed
standard_pcs = total_psc/zone_num*standard_num/100
standard_order = total_order/zone_num*standard_num/100

length = len(f_count_df)

zone_dict = {i: {"tot_pcs": 0, "tot_order": 0, "sku_codes": []} for i in range(1, zone_num+1)}
zone_list = np.zeros(length)

# add 30% 우선 채우기 부분
cut_ind = length/zone_num*0.2
inverse_dict = dict(zip(range(zone_num-1, -1, -1), range(1, zone_num+1)))

for i in range(length):
    row = f_count_df.iloc[i]
    if row["개수: 오더번호"] > standard_order and row["합계: pcs출하"] > standard_pcs:
        total_order -= row["개수: 오더번호"]
        total_psc -= row["합계: pcs출하"]
    else:
        if i > cut_ind and (i//zone_num)%2:
            ind = i%zone_num
            zone_dict[ind+1]["sku_codes"].append(row["Sku Code"])
            zone_dict[ind+1]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[ind+1]["tot_order"] += row["개수: 오더번호"]
        elif i > cut_ind and not((i//zone_num)%2):
            ind = i%zone_num
            zone_dict[inverse_dict[ind]]["sku_codes"].append(row["Sku Code"])
            zone_dict[inverse_dict[ind]]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[inverse_dict[ind]]["tot_order"] += row["개수: 오더번호"]
        else:
            min_zone = min(zone_dict, key=lambda x: zone_dict[x]["tot_pcs"])
            zone_dict[min_zone]["sku_codes"].append(row["Sku Code"])
            zone_dict[min_zone]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[min_zone]["tot_order"] += row["개수: 오더번호"]

for key, value in zone_dict.items():
    print(key, len(value["sku_codes"]), round(value["tot_pcs"]/total_psc*100, 2), round(value["tot_order"]/total_order*100, 2))

# 많은 친구는 뒤에 배치할 것(앞에서 밀리는 것 보다는 뒤에 배치하는게 좋음 )
sorted_zone_dict = dict(zip(sorted(zone_dict.keys(), key=lambda x: zone_dict[x]["tot_pcs"], reverse=True), [i for i in range(zone_num, 0, -1)]))

#remake zone_dict into "sku_code": "zone"
f_zone_dict = {}
for key, value in zone_dict.items():
    for sku_code in value["sku_codes"]:
        f_zone_dict[sku_code] = sorted_zone_dict[key]

#merge f_zone_dict to zone_list
for sku_code in f_zone_dict.keys():
    index = f_count_df[f_count_df["Sku Code"] == sku_code].index[0]
    zone_list[index] = f_zone_dict[sku_code]

f_count_df["zone 할당"] = zone_list
f_count_df.to_csv('data/LA_givendata_sample_7.csv', index=False)