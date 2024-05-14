import pandas as pd
import numpy as np
import random

seed = 42 #should be inputed
random.seed(seed)

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
length = len(f_count_df)

standard_pcs = total_psc/zone_num
standard_order = total_order/zone_num
standard_sku_count = int(length/zone_num)
# print(standard_pcs, standard_order, standard_sku_count)

plt_cut = 31.5 #should be inputed
plt_cut_pcs = standard_pcs*plt_cut/100
plt_cut_order = standard_order*plt_cut/100
# print(plt_cut_pcs, plt_cut_order)

zone_dict = {i: {"tot_pcs": 0, "tot_order": 0, "sku_codes": []} for i in range(1, zone_num+1)}
zone_list = np.zeros(length)
inverse_dict = dict(zip(range(zone_num-1, -1, -1), range(1, zone_num+1)))

def alert_differ(sku, order, pcs):
    if pcs > order*1.3:
        print(f"Alert: {sku} can be a problem. pcs: {pcs}, order: {order}")
    else:
        return None

range_indices = [i for i in range(length)]
c_range_indices = range_indices.copy()

for i in c_range_indices:
    row = f_count_df.iloc[i]
    if row["합계: pcs출하"] > plt_cut_pcs and row["개수: 오더번호"] > plt_cut_order:
        total_order -= row["개수: 오더번호"]
        total_psc -= row["합계: pcs출하"]
        range_indices.remove(i)
        alert_differ(row["Sku Code"], row["개수: 오더번호"], row["합계: pcs출하"])
    else:
        continue

trial_row = 5
cut_ind = zone_num*trial_row
fixed_range_indices = range_indices[:cut_ind]
random_range_indices = range_indices[cut_ind:]
c_random_range_indices = random_range_indices.copy()

for i in fixed_range_indices:
    row = f_count_df.iloc[i]
    if (i//zone_num)%2:
        ind = i%zone_num
        zone_dict[ind+1]["sku_codes"].append(row["Sku Code"])
        zone_dict[ind+1]["tot_pcs"] += row["합계: pcs출하"]
        zone_dict[ind+1]["tot_order"] += row["개수: 오더번호"]
    elif not((i//zone_num)%2):
        ind = i%zone_num
        zone_dict[inverse_dict[ind]]["sku_codes"].append(row["Sku Code"])
        zone_dict[inverse_dict[ind]]["tot_pcs"] += row["합계: pcs출하"]
        zone_dict[inverse_dict[ind]]["tot_order"] += row["개수: 오더번호"]

# get 
for zone_i in zone_dict.keys():
    upper_limit_order = standard_order*1.05 - zone_dict[zone_i]["tot_order"]
    lower_limit_order = standard_order*0.95 - zone_dict[zone_i]["tot_order"]
    upper_limit_sku = standard_sku_count + 2 - len(zone_dict[zone_i]["sku_codes"])
    lower_limit_sku = standard_sku_count - 2 - len(zone_dict[zone_i]["sku_codes"])

    for trial_rand in range(length):
        num_indices = random.randint(lower_limit_sku, upper_limit_sku)
        selected_indices = random.sample(c_random_range_indices, num_indices)
        print(selected_indices)
        sum_order = sum([f_count_df.iloc[j]["개수: 오더번호"] for j in selected_indices])
        print(sum_order + zone_dict[zone_i]["tot_order"])
        if sum_order > lower_limit_order and sum_order < upper_limit_order:
            for j in selected_indices:
                row = f_count_df.iloc[j]
                zone_dict[zone_i]["sku_codes"].append(row["Sku Code"])
                zone_dict[zone_i]["tot_pcs"] += row["합계: pcs출하"]
                zone_dict[zone_i]["tot_order"] += row["개수: 오더번호"]
                random_range_indices.remove(j)
        else:
            continue

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