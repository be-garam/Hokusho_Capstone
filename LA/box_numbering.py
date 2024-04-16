import pandas as pd

raw_df = pd.read_csv('data/LA_givendata_sample.csv')
df = raw_df.copy()

# B2B 구분
df["B2C구분"] = [i[:3] for i in df["주문Code1"]]

# 수량의 부피 계산
df["단위부피"] = df["가로(mm)"] * df["세로(mm)"] * df["높이(mm)"] * 10**(-6)
df["수량의 부피"] = df["pcs출하"] * df["단위부피"]

# 요청사항: B2C 구분, 수량의 부피 업데이트
df.to_csv('data/LA_givendata_sample_1.csv', index=False)

# Groupby 오더번호 and calculate the number of unique Sku Code, sum of 수량의 부피, and B2C구분
pregrouped_df = df[["오더번호", "B2C구분", "Sku Code", "수량의 부피"]]
grouped_df = pregrouped_df.groupby("오더번호").agg({"오더번호": "first", "Sku Code": "nunique", "수량의 부피": "sum", "B2C구분": lambda x: list(x)[0]})
grouped_df = grouped_df.rename(columns={"Sku Code": "개수: Sku Code", "수량의 부피": "합계: 수량의 부피"})
grouped_df = grouped_df.sort_values(by="합계: 수량의 부피", ascending=False)
# print(grouped_df.head())    
grouped_df.to_csv('data/LA_givendata_sample_2.csv', index=False)

# filterring df with grouped_df's "합계: 수량의 부피" and "B2C구분"
filtered_box = {}
for i in zip(grouped_df["오더번호"], grouped_df["합계: 수량의 부피"], grouped_df["B2C구분"]):
    if i[2] == "B2B" and i[1] >= 55.80:
        filtered_box[i[0]] = "*"
    elif i[2] == "B2C" and i[1] >= 53.41:
        filtered_box[i[0]] = "**"
    else:
        continue

# update the filtered box to the original df
df["1박스이상되는 주문_표시"] = df["오더번호"].map(filtered_box)
df["index"] = df.index
df.to_csv('data/LA_givendata_sample_3.csv', index=False)

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

box_index = df[df["1박스이상되는 주문_표시"].isin(["*", "**"])].groupby("오더번호")["index"].apply(list).to_dict()
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
df.to_csv('data/LA_givendata_sample_4.csv', index=False)
