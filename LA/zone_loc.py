import pandas as pd
import numpy as np

df_zoneloc = pd.read_csv('data/zone_location.csv')
# print(df_zoneloc.head())

zoneloc_list = df_zoneloc['location'].tolist()
zoneloc_list = [x.split("-") for x in zoneloc_list]

zone_list = [zone[0] for zone in zoneloc_list]
# print(zone_list)

#make count list base on zone_list and df_zoneloc's Sku code
sku_code_list = df_zoneloc['Sku Code'].tolist()
zone_sku_dict = {}  
zone_count_dict = {}
for i in range(len(zone_list)):
    zone = zone_list[i]
    sku_code = sku_code_list[i]
    if zone not in zone_sku_dict:
        zone_sku_dict[zone] = [sku_code]
        zone_count_dict[zone] = 1
    else:
        zone_sku_dict[zone].append(sku_code)
        zone_count_dict[zone] += 1

print(zone_count_dict)
print(sorted(zone_sku_dict.keys()))

# check plt list
pre_df_plt = pd.read_csv('data/LA_givendata_sample_7.csv')
print(pre_df_plt.head())
# get "Zone 할당" column's value is 0
df_plt = pre_df_plt[pre_df_plt['zone 할당'] == 0]
plt_list = df_plt["Sku Code"].tolist()

plt_zone_list = [df_zoneloc[df_zoneloc['Sku Code'] == plt]['location'].values[0].split("-")[0] for plt in plt_list]
print(plt_zone_list)