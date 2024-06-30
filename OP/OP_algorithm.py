# functions

# rank_analysis (2023 ver.)
def rank_analysis(data, rank, order):
    import pandas as pd
    import numpy as np
    import time, datetime
    start = time.time()

    ################# 주문패턴 (Rank pattern) 부여 #################
    op_frame = data.groupby(order)[rank].unique().to_frame()
    op_frame['Rank패턴'] = np.nan
    for i in range(len(op_frame)):
        rank_list = op_frame.iloc[i][rank]

        if 'A' in rank_list:
            if 'B' in rank_list:
                if 'C' in rank_list:
                    op_frame.iloc[i, 1] = 'pattern7'
                else:
                    op_frame.iloc[i, 1] = 'pattern4'
            elif 'C' in rank_list:
                op_frame.iloc[i, 1] = 'pattern5'
            else:
                op_frame.iloc[i, 1] = 'pattern1'
        elif 'B' in rank_list:
            if 'C' in rank_list:
                op_frame.iloc[i, 1] = 'pattern6'
            else:
                op_frame.iloc[i, 1] = 'pattern2'
        else:
            op_frame.iloc[i, 1] = 'pattern3'

    try:
        data['Rank패턴'] = data[order]
        for i in range(len(data)):
            data.iloc[i, -1] = op_frame.loc[data.iloc[i, -1]][1]
        print('Rank 패턴 분류를 완료하였습니다.')

        end = time.time()
        print('소요된 시간: ', datetime.timedelta(seconds=end - start))
        print('')
        return data
    except:
        print('Rank 패턴 분류에 문제가 생겼습니다. 데이터를 다시 확인해주세요.')
        return

def equip_analysis(data, order, sku, quantity, rank, tolerance=0.05, max_iter=10**5, save_name='OP_result',
                   exchange_ratio=0.1, OTP_ratio={'A': [0.5, 0.5],'B': [0.5, 0.5]}, SEP_ratio=[0.5, 0.5]):
    import pandas as pd
    try:
        # A 랭크에 대한 예외 처리
        a = int(set(OTP_ratio['A']) != {0})  # a=0인 경우, A 랭크가 0인 것.
        if a == 0:
            data = data[data[rank] != 'A']
            OTP_ratio['A'] = [0 for i in range(len(OTP_ratio['B']))]

        # OTP와 SEP 데이터 분리
        OTP = data[data[rank] != 'C']
        SEP = data[data[rank] == 'C']

        # qty 저장
        OTP_qty = int(OTP[quantity].sum() / len(OTP_ratio['B']))
        SEP_qty = int(SEP[quantity].sum() / len(SEP_ratio))

        # OTP A와 B 분리
        OTP_A = OTP[OTP[rank] == 'A']
        OTP_B = OTP[OTP[rank] == 'B']

        # sku 기준 grouping
        OTP_A_grouped = pd.DataFrame(OTP_A.groupby(sku)[quantity].sum()).reset_index()
        OTP_B_grouped = pd.DataFrame(OTP_B.groupby(sku)[quantity].sum()).reset_index()
        SEP_grouped = pd.DataFrame(SEP.groupby(sku)[quantity].sum()).reset_index()

        # 비율에 따른 분할
        if a==0:
            splited_A = [pd.DataFrame(columns=OTP_A_grouped.columns) for i in range(len(OTP_ratio['A']))]  # 빈 array의 리스트
        else:
            splited_A = initial_split_sku(OTP_A_grouped, OTP_ratio['A'], quantity)
        splited_B = initial_split_sku(OTP_B_grouped, OTP_ratio['B'], quantity)
        splited_C = initial_split_sku(SEP_grouped, SEP_ratio, quantity)

        # OTP에 대한 할당
        final_A, final_B = quantity_adjust_OTP(splited_A, splited_B, quantity, sku, a, tolerance, max_iter, exchange_ratio)

        # SEP에 대한 할당
        final_C = quantity_adjust_SEP(splited_C, quantity, sku, tolerance, max_iter, exchange_ratio)

        # 패턴 라벨링
        grouped_A = pattern_labelling(final_A, 'OTP', 'A', sku) # a=0인 경우 empty
        grouped_B = pattern_labelling(final_B, 'OTP', 'B', sku)
        grouped_C = pattern_labelling(final_C, 'SEP', 'C', sku)

        # merge
        merged_A = data.merge(grouped_A, on=sku, how='left') # a=0인 경우 A 랭크가 없는 데이터
        merged_B = merged_A.merge(grouped_B, on=sku, how='left')
        merged_C = merged_B.merge(grouped_C, on=sku, how='left')

        merged_C['EQUIP'] = merged_C['OTP_A'].combine_first(merged_C['OTP_B']).combine_first(merged_C['SEP_C'])
        order_categories = merged_C.groupby(order)['EQUIP'].apply(lambda x: ''.join(sorted(set(x)))).reset_index()
        order_categories['EQUIP패턴'] = 'pattern' + (order_categories.groupby('EQUIP').ngroup() + 1).astype(str)
        final_DF = merged_C.merge(order_categories[[order, 'EQUIP패턴']], on=order)

        use = [order, sku, quantity, rank, 'Rank패턴', 'EQUIP', 'EQUIP패턴']

        final = final_DF[use].astype({'SKU':'string'})

        print(f'Alert: Start saving...')
        final[use].to_excel(f'{save_name}.xlsx', index=False, encoding='cp949', engine='openpyxl')
        print('Alert: ALL DONE!(please check your files)\n')
    except:
        print('Alert: please check your data(equip_analysis)')

def initial_split_sku(grouped, ratios, quantity):
    try:
        import numpy as np
        shuffled = np.random.permutation(grouped.index) # 랜덤성 부여
        row_num = len(grouped)
        group_sizes = [int(row_num * ratio) for ratio in ratios]
        splits = np.split(shuffled, np.cumsum(group_sizes)[:-1]) # 해당 랭크의 비율에 맞게 쪼개기
        splited = [grouped.iloc[split] for split in splits]
        splited_sorted = [splited_frag.sort_values(by=quantity, ascending=False) for splited_frag in splited]
        return splited_sorted
    except:
        print('Alert: please check your data(initial_split_sku)')

def quantity_adjust_OTP(splited_A, splited_B, quantity, sku, a=1, tolerance=0.05, max_iter=10 ** 5, exchange_ratio=0.1):
    try:
        import pandas as pd
        import numpy as np
        import time, datetime
        start = time.time()

        # qty 계산
        if a:
            A_qty_list = [i[quantity].sum() for i in splited_A]
            A_sku_min = min([len(i[sku]) for i in splited_A])
        else:
            A_qty_list = [0 for i in splited_B]
            A_sku_min = 0
        B_qty_list = [i[quantity].sum() for i in splited_B]
        total_qty_list = [A_qty_list[i] + B_qty_list[i] for i in range(len(splited_B))]
        ideal_qty = int(sum(total_qty_list) / len(total_qty_list))
        B_sku_min = min([len(i[sku]) for i in splited_B])

        iteration = 0
        print(f'Alert: Start iteration...')

        while iteration <= max_iter:
            # max와 min 그룹의 인덱스 구하기
            min_idx = total_qty_list.index(min(total_qty_list))
            max_idx = total_qty_list.index(max(total_qty_list))

            # 차이 계산
            diff_min = abs(ideal_qty - total_qty_list[min_idx]) / ideal_qty
            diff_max = abs(ideal_qty - total_qty_list[max_idx]) / ideal_qty

            # qty값 조정
            if diff_min > tolerance or diff_max > tolerance:
                # 교환 비율 지정: 10%로!
                if a:
                    slice_min_A = int(A_sku_min * max(diff_min, diff_max))
                    slice_min_A = int(A_sku_min * exchange_ratio)
                    splited_A[min_idx].iloc[-(slice_min_A + 1):-1], splited_A[max_idx].iloc[0:slice_min_A] = splited_A[max_idx].iloc[0:slice_min_A].copy(), splited_A[min_idx].iloc[-(slice_min_A + 1):-1].copy()

                slice_min_B = int(B_sku_min * max(diff_min, diff_max))
                slice_min_B = int(B_sku_min * exchange_ratio)
                splited_B[min_idx].iloc[-(slice_min_B + 1):-1], splited_B[max_idx].iloc[0:slice_min_B] = splited_B[max_idx].iloc[0:slice_min_B].copy(), splited_B[min_idx].iloc[-(slice_min_B + 1):-1].copy()

            else:
                print(f"Alert: Ideally divided! (tolerance={tolerance * 100}%)\n")
                break

            # 다음 반복 위한 처리
            if a:
                A_qty_list = [i[quantity].sum() for i in splited_A]
                splited_A = [frag.sort_values(by=quantity, ascending=False) for frag in splited_A]

            B_qty_list = [i[quantity].sum() for i in splited_B]
            total_qty_list = [A_qty_list[i] + B_qty_list[i] for i in range(len(splited_B))]
            splited_B = [frag.sort_values(by=quantity, ascending=False) for frag in splited_B]

            iteration += 1

            if iteration > max_iter:
                print(f"Alert: May not be equally divided")
                print('===========================')
                print(f'minimum difference: {round(diff_min, 3)}\nmaximum difference: {round(diff_max, 3)}')
                print('===========================\n')

        end = time.time()

        ##### results
        print('QUANTITY')
        print('===========================')
        print(f'IDEAL: {ideal_qty}')
        for i in range(len(total_qty_list)):
            qty = splited_A[i][quantity].sum() + splited_B[i][quantity].sum()
            print(f'OTP {i + 1}: {qty}')
        print('===========================')

        print('')
        print('TIME')
        print('===========================')
        print(datetime.timedelta(seconds=end - start))
        print('===========================\n')

        return splited_A, splited_B
    except:
        print('Alert: please check your data(quantity_adjust_OTP)')


def quantity_adjust_SEP(splited_C, quantity, sku, tolerance=0.05, max_iter=10 ** 5, exchange_ratio=0.1):
    try:
        import pandas as pd
        import numpy as np
        import time, datetime
        start = time.time()

        # qty 계산
        qty_list = [i[quantity].sum() for i in splited_C]
        ideal_qty = int(sum(qty_list) / len(qty_list))
        sku_min = min([len(i[sku]) for i in splited_C])

        iteration = 0
        print(f'Alert: Start iteration...')

        while iteration <= max_iter:  # test 데이터 기준으로 다 도는 데 약 4분 소요.
            # max와 min 그룹의 인덱스 구하기
            min_idx = qty_list.index(min(qty_list))
            max_idx = qty_list.index(max(qty_list))

            # 차이 계산
            diff_min = abs(ideal_qty - qty_list[min_idx]) / ideal_qty
            diff_max = abs(ideal_qty - qty_list[max_idx]) / ideal_qty

            # qty값 조정
            if diff_min > tolerance or diff_max > tolerance:
                # 교환 비율 지정: 10%로!
                slice_min = int(sku_min * exchange_ratio)
                # 교환
                splited_C[min_idx].iloc[-(slice_min + 1):-1], splited_C[max_idx].iloc[0:slice_min] = splited_C[max_idx].iloc[0:slice_min].copy(), splited_C[min_idx].iloc[-(slice_min + 1):-1].copy()
            else:
                print(f"Alert: Ideally divided! (tolerance={tolerance * 100}%)\n")
                break

            # 다음 반복 위한 처리
            qty_list = [i[quantity].sum() for i in splited_C]
            splited_C = [frag.sort_values(by=quantity, ascending=False) for frag in splited_C]

            iteration += 1

            if iteration > max_iter:
                print(f"Alert: May not be equally divided")
                print('===========================')
                print(f'minimum difference: {round(diff_min, 3)}\nmaximum difference: {round(diff_max, 3)}')
                print('===========================\n')

        end = time.time()

        ##### results
        print('QUANTITY')
        print('===========================')
        print(f'IDEAL: {ideal_qty}')
        for i in range(len(qty_list)):
            qty = splited_C[i][quantity].sum()
            print(f'SEP {i + 1}: {qty}')
        print('===========================')

        print('')
        print('TIME')
        print('===========================')
        print(datetime.timedelta(seconds=end - start))
        print('===========================\n')

        return splited_C
    except:
        print('Alert: please check your data(quantity_adjust_SEP)')

def pattern_labelling(data, equip, rank, sku):
    import pandas as pd
    try:
        grouped = []
        for num, df in enumerate(data):
            data[num][f'{equip}_{rank}'] = f'{equip} {num + 1}'
            grouped.append(data[num])

        grouped = pd.concat(grouped, ignore_index=True)[[sku, f'{equip}_{rank}']]
        return grouped
    except:
        print('Alert: please check your data(pattern_labelling)')


### 메인 함수
def OP_main(data, order, sku, quantity, rank, tolerance=0.05, max_iter=10**5,
            save_name='OP_result', exchange_ratio=0.1,
            OTP_ratio={'A': [0.5, 0.5],'B': [0.5, 0.5]}, SEP_ratio=[0.5, 0.5]):
    try:
        ranked_data = rank_analysis(data, rank, order)
        print("Alert: DONE function ranked_data\n")
        equip_analysis(ranked_data, order, sku, quantity, rank, tolerance=tolerance, max_iter=max_iter,
                       save_name=save_name, exchange_ratio=exchange_ratio, OTP_ratio=OTP_ratio, SEP_ratio=SEP_ratio)
    except:
        print('Alert: please check your data(OP_main)')

if __name__ == '__main__':
    import pandas as pd
    import numpy as np

    # 예시 데이터
    order = 'ORDERKEY'
    sku = 'SKU'
    rank = 'Rank'
    quantity = 'QTYEXPECTED'
    columns_to_load = [order, sku, rank, quantity]
    data_dir = "./data/OP_Sample_1203_raw_data.xlsx"
    data = pd.read_excel(data_dir, usecols=columns_to_load)

    # main execution
    OP_main(data, order, sku, quantity, rank, save_name="OP_test")
