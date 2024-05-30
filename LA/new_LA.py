# import whole function for location-assigment.py
from location_assignment import *
import pandas as pd
import numpy as np
import random
import sys
import os
import openpyxl

def filter_df(df):
    #filtering row with value A in column "Rank"
    df = df[df["Rank"] == "A"]
    return df


def __main__():
    seed = 42 #maybe random
    random.seed(seed)
    width = 80

    path, raw_df = check_df()
    pre_df = raw_df.copy()
    box_filtered_df = filter_df(pre_df)

    pcs_col_name, sku_col_name = "수량", "상품코드"
    base_dir = 'output/'
    file_name = path.split('/')[-1].split('.')[0]
    file_type = '_LA.xlsx'
    xlxs_dir = os.path.join(base_dir, file_name+file_type)
    # print("checking the columns".center(width, "="))
    # pre_b2c_col_name, order_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name, sku_col_name = check_column(pre_df)
    
    print("getting the parameters".center(width, "="))
    b2b_min, b2c_min, plt_cut, zone_num, trial_row, error_percentage = get_parameters()

    # b2c_volume_df = update_b2c_volume(pre_df, width, pre_b2c_col_name, width_col_name, height_col_name, depth_col_name, pcs_col_name)
    # b2c_grouped_df = classify_b2c(b2c_volume_df, width, order_col_name, sku_col_name)
    # b2c_grouped_df.to_csv('output/LA_오더의_박스수_정하기.csv', index=False)

    # box_filtered_df = filtering_box(b2c_grouped_df, b2c_volume_df, width, order_col_name, b2b_min, b2c_min)

    df_grouped = group_order_pcs(box_filtered_df, pcs_col_name, sku_col_name)
    df_grouped, df_plt, total_psc, total_order, length = cutting_plt(df_grouped, sku_col_name, plt_cut, zone_num)
    df_grouped = zone_assignment(df_grouped, sku_col_name, zone_num, trial_row, error_percentage, total_psc, total_order, length)
    
    zone_df = pd.concat([df_plt, df_grouped], ignore_index=True)
    zone_df.to_csv(base_dir + file_name + '배치zone할당.csv', index=False)

    final_df = merge_zone(box_filtered_df, zone_df, sku_col_name)

    # print(final_df.columns)

    # final_df.drop(columns=["index"], inplace=True)
    final_df.to_csv(base_dir+file_name+file_type, index=False)

    with pd.ExcelWriter(xlxs_dir) as writer:
        final_df.to_excel(writer, sheet_name = '요청자료')
        # b2c_grouped_df.to_excel(writer, sheet_name = '오더의 박스수 정하기')
        zone_df.to_excel(writer, sheet_name = '품목_배치zone할당')

if __name__ == "__main__":
    __main__()