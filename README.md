# Hokusho_Capstone
2024-1 Hokusho Capstone Design Project

## File Tree
```
├── BA 
│   ├── README.md
│   ├── data
│   └── BA.ipynb
├── LA
│   ├── README.md
│   ├── data
│   └── BA.ipynb
├── OP 
│   ├── README.md
│   ├── data
│   └── BA.ipynb
└── OriginData
```
### OriginData
- 보안을 위해 원본은 하나의 폴더에서 처리하며 업로드 되지 않도록 처리
    - [google drive](https://drive.google.com/drive/folders/1P2j-dSsQaF8GGx-Mq3gI51K6zda--sYc?usp=drive_link)
- OS단의 인코딩, 디코딩 에러 방지를 위해 각 파일명을 아래와 같이 변경
    - 주문패턴: Order pattern
        - OP_Sample_OilveYoung_0603_rank_B_EQ.xlsx: 주문패턴할당용 샘플_올리브영_행사_출고_6월03일자+rank및 B설비_EQ.xlsx
        - OP_Sample_1203_raw_data.xlsx: 주문패턴할당용 샘플_1203 합포_작업용_raw data.xlsx
    - 배치할당: Batch Assignment
        - BA_Sample_Samsung_0421_raw_data.xlsx: 배치할당용 샘플_삼성물산_출하_4월21일자_raw data.xlsx
        - BA_Sample_Samsung_0421_verificated_60suit.xlsx: 배치할당용 샘플_삼성물산_출하_4월21일자_검증확인2_60슈트(48~51배치).xlsx
        - BA_Sample_Samsung_0421_verificated_1.xlsx: 배치할당용 샘플_삼성물산_출하_4월21일자_검증확인1.xlsx
    - 로케이션할당: Location Assignment
        - LA_Sample_Taiwan_Pantos_Atomy_Performance_0307.xlsx: 로케이션할당용 샘플_대만판토스_애터미 실적Data (0307)_1.xlsx
        
### 배치 할당: BA
- R&R: Harin & tnsu37
- move to [BA description](/BA/Readme.md)

### 로케이션 할당: LA
- R&R: be-garam
- move to [LA description](/LA/Readme.md)

### 주문 패턴: OP
- R&R: Harin & tnsu37
- move to [OP description](/OP/Readme.md)
