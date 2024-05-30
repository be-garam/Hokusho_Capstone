import pandas as pd
import numpy as np
import random
import sys
# import argparse

def check_df():
    path = input("Enter the path of the csv file: ")
    try:
        path = str(path) if path else "data/LA_givendata_sample.csv"
        df = pd.read_csv(path)
    except:
        print("Please enter a valid path.")
        sys.exit()
    return path, df


def validate_column(df, col_name):
    try:
        df[col_name]
    except:
        print(f"{col_name} is not in the dataframe.")
        sys.exit()


def check_column(df):
    pre_b2c_col = input("Enter the column name for 주문Code1(if you just enter, 주문Code1 will be setted): ")
    pre_b2c_col_name = "주문Code1" if not pre_b2c_col else pre_b2c_col
    validate_column(df, pre_b2c_col_name)

    order_col = input("Enter the column name for 오더번호(if you just enter, 오더번호 will be setted): ")
    order_col_name = "오더번호" if not order_col else order_col
    validate_column(df, order_col_name)

    width_col = input("Enter the column name for 가로(mm)(if you just enter, 가로(mm) will be setted): ")
    width_col_name = "가로(mm)" if not width_col else width_col
    validate_column(df, width_col_name)

    height_col = input("Enter the column name for 세로(mm)(if you just enter, 세로(mm) will be setted): ")
    height_col_name = "세로(mm)" if not height_col else height_col
    validate_column(df, height_col_name)

    depth_col = input("Enter the column name for 높이(mm)(if you just enter, 높이(mm) will be setted): ")
    depth_col_name = "높이(mm)" if not depth_col else depth_col
    validate_column(df, depth_col_name)

    pcs_col = input("Enter the column name for pcs출하(if you just enter, pcs출하 will be setted): ")
    pcs_col_name = "pcs출하" if not pcs_col else pcs_col
    validate_column(df, pcs_col_name)

    sku_col = input("Enter the column name for Sku Code(if you just enter, Sku Code will be setted): ")
    sku_col_name = "Sku Code" if not sku_col else sku_col
    validate_column(df, sku_col_name)

    return pre_b2c_col_name, order_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name, sku_col_name


def get_parameters():
    b2b_min = input("Enter the minimum volume of B2B(default will be 55.80): ")
    b2c_min = input("Enter the minimum volume of B2C(default will be 53.41): ")

    try:
        b2b_min = float(b2b_min) if b2b_min else 55.80
        b2c_min = float(b2c_min) if b2c_min else 53.41
    except:
        print("Please enter a valid number.")
        sys.exit()
    
    plt_cut = input("Enter the percentage of plt cut(default will be 31.5): ")
    zone_num = input("Enter the number of zones(default will be 10): ")
    trial_row = input("Enter the number of trial rows(default will be 3): ")
    error_percentage = input("Enter the error percentage(default will be 0.05): ")

    try:
        plt_cut = float(plt_cut) if plt_cut else 31.5
        zone_num = int(zone_num) if zone_num else 10
        trial_row = int(trial_row) if trial_row else 3
        error_percentage = float(error_percentage) if error_percentage else 0.05
    except:
        print("Please enter a valid number.")
        sys.exit()

    return b2b_min, b2c_min, plt_cut, zone_num, trial_row, error_percentage


def update_b2c_volume(df, width, pre_b2c_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name):
    df["B2C구분"] = [i[:3] for i in df[pre_b2c_col_name]]
    print("B2C구분 업데이트 완료".center(width, "="))

    df["단위부피"] = df[width_col_name] * df[height_col_name] * df[depth_col_name] * 10**(-6)
    print("단위부피 업데이트 완료".center(width, "="))

    df["수량의 부피"] = df[pcs_col_name] * df["단위부피"]
    print("수량의 부피 업데이트 완료".center(width, "="))

    return df


def classify_b2c(df, width, order_col_name, sku_col_name):
    pregrouped_df = df[[order_col_name, "B2C구분", sku_col_name, "수량의 부피"]]
    grouped_df = pregrouped_df.groupby(order_col_name).agg({order_col_name: "first", sku_col_name: "nunique", "수량의 부피": "sum", "B2C구분": lambda x: list(x)[0]})
    grouped_df = grouped_df.rename(columns={sku_col_name: "개수: Sku Code", "수량의 부피": "합계: 수량의 부피"})
    grouped_df = grouped_df.sort_values(by="합계: 수량의 부피", ascending=False)
    # grouped_df.drop("오더번호", axis=1, inplace=True)

    print("오더의 박스수 정하기 완료".center(width, "="))
    return grouped_df


def create_boxes(index_voulumn_dict, standard):
    boxes = []
    current_box = []
    total = 0

    volumn_list = index_voulumn_dict.keys()

    for value in volumn_list:
        if total + value <= standard:
            current_box.append(index_voulumn_dict[value])
            total += value
        else:
            boxes.append(current_box)
            current_box = [index_voulumn_dict[value]]
            total = value

    if current_box:
        boxes.append(current_box)

    return boxes


def filtering_box(grouped_df, df, width, order_col_name, b2b_min, b2c_min):
    filtered_box = {}
    for i in zip(grouped_df[order_col_name], grouped_df["합계: 수량의 부피"], grouped_df["B2C구분"]):
        if i[2] == "B2B" and i[1] >= b2b_min:
            filtered_box[i[0]] = "*"
        elif i[2] == "B2C" and i[1] >= b2c_min:
            filtered_box[i[0]] = "**"
        else:
            continue

    # update the filtered box to the original df
    df["1박스이상되는 주문_표시"] = df[order_col_name].map(filtered_box)
    df["index"] = df.index

    box_index = df[df["1박스이상되는 주문_표시"].isin(["*", "**"])].groupby(order_col_name)["index"].apply(list).to_dict()
    df_boxnum = [None for _ in range(len(df))]

    for key, value in box_index.items():
        if df.loc[value[0], "1박스이상되는 주문_표시"] == "*":
            index_voulumn_dict = {df.loc[i, "수량의 부피"]:i for i in value}
            box_list = create_boxes(index_voulumn_dict, 55.80)
            for index, box in enumerate(box_list):
                for i in box:
                    df_boxnum[i] = index + 1
        elif df.loc[value[0], "1박스이상되는 주문_표시"] == "**":
            index_voulumn_dict = {df.loc[i, "수량의 부피"]:i for i in value}
            box_list = create_boxes(index_voulumn_dict, 53.41)
            for index, box in enumerate(box_list):
                for i in box:
                    df_boxnum[i] = index + 1
        else:
            continue

    df["박스번호"] = df_boxnum

    return df


def group_order_pcs(df_boxnum, pcs_col_name, sku_col_name):
    grouped_dict = {}
    for i in range(len(df_boxnum)):
        row = df_boxnum.iloc[i]
        sku_code = row[sku_col_name]
        pcs = row[pcs_col_name]
        if sku_code in grouped_dict.keys():
            grouped_dict[sku_code][0] += 1
            grouped_dict[sku_code][1] += pcs
        else:
            grouped_dict[sku_code] = [1, pcs]

    df_grouped = pd.DataFrame.from_dict(grouped_dict, orient="index", columns=["개수: 오더번호", "합계: pcs출하"]).reset_index()
    df_grouped.columns = [sku_col_name, "개수: 오더번호", "합계: pcs출하"]
    # df_grouped = df_grouped.sort_values(by="개수: 오더번호", ascending=False).reset_index()

    return df_grouped


def alert_differ(sku, order, pcs):
    if pcs > order*1.3:
        print(f"Alert: {sku} can be a problem. pcs: {pcs}, order: {order}")
    else:
        return None


def cutting_plt(df_grouped, sku_col_name, plt_cut, zone_num):
    total_psc = sum(df_grouped["합계: pcs출하"])
    total_order = sum(df_grouped["개수: 오더번호"])
    length = len(df_grouped)
    # print(f"before / total_psc: {total_psc}, total_order: {total_order}, length: {length}")

    plt_cut_pcs = total_psc/zone_num*plt_cut/100
    plt_cut_order = total_order/zone_num*plt_cut/100

    df_plt = pd.DataFrame(columns=[sku_col_name, "개수: 오더번호", "합계: pcs출하"])
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


def zone_assignment(df_grouped, sku_col_name, zone_num, trial_row, error_percentage, total_psc, total_order, length):

    standard_pcs = total_psc/zone_num
    standard_order = total_order/zone_num
    standard_sku_count = int(length/zone_num)

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
            zone_dict[ind+1]["sku_codes"].append(row[sku_col_name])
            zone_dict[ind+1]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[ind+1]["tot_order"] += row["개수: 오더번호"]
            zone_dict[ind+1]["ind"].append(i)
        elif not((i//zone_num)%2):
            ind = i%zone_num
            zone_dict[inverse_dict[ind]]["sku_codes"].append(row[sku_col_name])
            zone_dict[inverse_dict[ind]]["tot_pcs"] += row["합계: pcs출하"]
            zone_dict[inverse_dict[ind]]["tot_order"] += row["개수: 오더번호"]
            zone_dict[ind+1]["ind"].append(i)
    
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
                    zone_dict[zone_i]["sku_codes"].append(row[sku_col_name])
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
        index = df_grouped[df_grouped[sku_col_name] == sku_code].index[0]
        zone_list[index] = f_zone_dict[sku_code]

    df_grouped["zone 할당"] = zone_list

    return df_grouped


def merge_zone(box_filtered_df, zone_df, sku_col_name):
    # merge zone_df's "zone 할당" to box_filtered_df based on "Sku Code"
    box_filtered_df = pd.merge(box_filtered_df, zone_df[[sku_col_name, "zone 할당"]], on=sku_col_name, how="left")
    return box_filtered_df

def __main__():
    seed = 42 #maybe random
    random.seed(seed)
    width = 80

    raw_df = check_df()
    pre_df = raw_df.copy()
    print("checking the columns".center(width, "="))
    pre_b2c_col_name, order_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name, sku_col_name = check_column(pre_df)
    
    print("getting the parameters".center(width, "="))
    b2b_min, b2c_min, plt_cut, zone_num, trial_row, error_percentage = get_parameters()

    b2c_volume_df = update_b2c_volume(pre_df, width, pre_b2c_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name)
    b2c_grouped_df = classify_b2c(b2c_volume_df, width, order_col_name, sku_col_name)
    b2c_grouped_df.to_csv('output/LA_오더의_박스수_정하기.csv', index=False)

    box_filtered_df = filtering_box(b2c_grouped_df, b2c_volume_df, width, order_col_name, b2b_min, b2c_min)

    df_grouped = group_order_pcs(box_filtered_df)
    df_grouped, df_plt, total_psc, total_order, length = cutting_plt(df_grouped, plt_cut, zone_num)
    df_grouped = zone_assignment(df_grouped, zone_num, trial_row, error_percentage, total_psc, total_order, length)
    
    zone_df = pd.concat([df_plt, df_grouped], ignore_index=True)
    zone_df.to_csv('output/LA_품목_배치zone할당.csv', index=False)

    final_df = merge_zone(box_filtered_df, zone_df)

    final_df.drop(columns=["index"], inplace=True)
    final_df.to_csv('output/LA_최종_요청자료.csv', index=False)

if __name__ == "__main__":
    __main__()