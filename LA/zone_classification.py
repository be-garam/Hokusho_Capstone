import pandas as pd
import numpy as np
import random
import sys
import argparse


def group_order_pcs(df_boxnum):
    grouped_dict = {}
    for i in range(len(df_boxnum)):
        row = df_boxnum.iloc[i]
        sku_code = row["Sku Code"]
        pcs = row["pcs출하"]
        if sku_code in grouped_dict.keys():
            grouped_dict[sku_code][0] += 1
            grouped_dict[sku_code][1] += pcs
        else:
            grouped_dict[sku_code] = [1, pcs]

    df_grouped = pd.DataFrame.from_dict(grouped_dict, orient="index", columns=["개수: 오더번호", "합계: pcs출하"]).reset_index()
    df_grouped.columns = ["Sku Code", "개수: 오더번호", "합계: pcs출하"]
    # df_grouped = df_grouped.sort_values(by="개수: 오더번호", ascending=False).reset_index()

    return df_grouped


# alert if pcs is more than 30% of order
def alert_differ(sku, order, pcs):
    if pcs > order*1.3:
        print(f"Alert: {sku} can be a problem. pcs: {pcs}, order: {order}")
    else:
        return None


def cutting_plt(df_grouped, plt_cut, zone_num):
    total_psc = sum(df_grouped["합계: pcs출하"])
    total_order = sum(df_grouped["개수: 오더번호"])
    length = len(df_grouped)
    # print(f"before / total_psc: {total_psc}, total_order: {total_order}, length: {length}")

    plt_cut_pcs = total_psc/zone_num*plt_cut/100
    plt_cut_order = total_order/zone_num*plt_cut/100

    df_plt = pd.DataFrame(columns=["Sku Code", "개수: 오더번호", "합계: pcs출하"])
    drop_index = []
    for i in range(length):
        row = df_grouped.iloc[i]
        if row["합계: pcs출하"] > plt_cut_pcs and row["개수: 오더번호"] > plt_cut_order:
            df_plt.loc[i] = row 
            total_order -= row["개수: 오더번호"]
            total_psc -= row["합계: pcs출하"]
            length -= 1
            drop_index.append(i)
        else:
            continue
    df_plt["zone 할당"] = ["PLT" for i in range(len(df_plt))]
    df_plt.reset_index(drop=True, inplace=True)
    # df_plt.to_csv('data/LA_givendata_sample_plt.csv', index=False)
    
    # print(f"after / total_psc: {total_psc}, total_order: {total_order}, length: {length}")
    df_grouped.drop(drop_index, inplace=True)
    df_grouped = df_grouped.sort_values(by="개수: 오더번호", ascending=False)
    df_grouped.reset_index(drop=True, inplace=True)
    # df_grouped.to_csv('data/LA_givendata_sample_plt_droped.csv', index=False)
    # print(df_grouped.head())
    return df_grouped, df_plt, total_psc, total_order, length


def zone_assignment(df_grouped, zone_num, trial_row, error_percentage, total_psc, total_order, length):

    standard_pcs = total_psc/zone_num
    standard_order = total_order/zone_num
    standard_sku_count = int(length/zone_num)

    print(f"standard_pcs: {standard_pcs}, standard_order: {standard_order}, standard_sku_count: {standard_sku_count}")

    # 12345/98765/
    cut_ind = zone_num*trial_row
    range_indices = [i for i in range(length)]
    fixed_range_indices = range_indices[:cut_ind]
    random_range_indices = range_indices[cut_ind:]
    c_random_range_indices = random_range_indices.copy()

    zone_dict = {i: {"ind":[], "tot_pcs": 0, "tot_order": 0, "sku_codes": []} for i in range(1, zone_num+1)}
    zone_list = np.zeros(length)
    inverse_dict = dict(zip(range(zone_num-1, -1, -1), range(1, zone_num+1)))

    for i in fixed_range_indices:
        row = df_grouped.iloc[i]
        if (i//zone_num)%2:
            ind = i%zone_num
            zone_dict[ind+1]["sku_codes"].append(row["Sku Code"])
            zone_dict[ind+1]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[ind+1]["tot_order"] += row["개수: 오더번호"]
            zone_dict[ind+1]["ind"].append(i)
        elif not((i//zone_num)%2):
            ind = i%zone_num
            zone_dict[inverse_dict[ind]]["sku_codes"].append(row["Sku Code"])
            zone_dict[inverse_dict[ind]]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[inverse_dict[ind]]["tot_order"] += row["개수: 오더번호"]
            zone_dict[ind+1]["ind"].append(i)
    
    print(zone_dict)
    # random
    for zone_i in zone_dict.keys():
        upper_limit_order = standard_order*(1.00 + error_percentage) - zone_dict[zone_i]["tot_order"]
        lower_limit_order = standard_order*(1.00 - error_percentage) - zone_dict[zone_i]["tot_order"]
        upper_limit_sku = standard_sku_count + 2 - len(zone_dict[zone_i]["sku_codes"])
        lower_limit_sku = standard_sku_count - 2 - len(zone_dict[zone_i]["sku_codes"])
        print(f"{zone_i}'s exisiting order: {zone_dict[zone_i]['tot_order']}, exisiting pcs: {zone_dict[zone_i]['tot_pcs']}")
        print(f"upper_limit_order: {upper_limit_order}, lower_limit_order: {lower_limit_order}")
        print(f"upper_limit_sku: {upper_limit_sku}, lower_limit_sku: {lower_limit_sku}")

        for trial_rand in range(10**6):
            num_indices = random.randint(lower_limit_sku, upper_limit_sku)
            selected_indices = random.sample(random_range_indices, num_indices)
            sum_order = sum([df_grouped.iloc[j]["개수: 오더번호"] for j in selected_indices])
            if sum_order > lower_limit_order and sum_order < upper_limit_order:
                print("selected_indices' sum: ", sum_order)
                for j in selected_indices:
                    row = df_grouped.iloc[j]
                    zone_dict[zone_i]["sku_codes"].append(row["Sku Code"])
                    zone_dict[zone_i]["tot_pcs"] += row["합계: pcs출하"]
                    zone_dict[zone_i]["tot_order"] += row["개수: 오더번호"]
                    random_range_indices.remove(j)
                break
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
        index = df_grouped[df_grouped["Sku Code"] == sku_code].index[0]
        zone_list[index] = f_zone_dict[sku_code]

    df_grouped["zone 할당"] = zone_list

    return df_grouped

def __main__(zone_num, plt_cut, trial_row, error_percentage):
    seed = 42 #should be inputed
    random.seed(seed)

    df_boxnum = pd.read_csv('data/LA_givendata_sample_4.csv')

    df_grouped = group_order_pcs(df_boxnum)
    df_grouped, df_plt, total_psc, total_order, length = cutting_plt(df_grouped, plt_cut, zone_num)
    df_grouped = zone_assignment(df_grouped, zone_num, trial_row, error_percentage, total_psc, total_order, length)
    
    zone_df = pd.concat([df_plt, df_grouped], ignore_index=True)
    zone_df.to_csv('data/LA_givendata_sample_zone.csv', index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="zone assignment with filtering plt")
    parser.add_argument("--zone_num", type=int, default=10)
    parser.add_argument("--plt_cut", type=int, default=31.5)
    parser.add_argument("--trial_row", type=int, default=2)
    parser.add_argument("--error_percentage", type=float, default=0.05)
    args = parser.parse_args()

    __main__(args.zone_num, args.plt_cut, args.trial_row, args.error_percentage)