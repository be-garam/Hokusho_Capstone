from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidget, QTableWidgetItem,
                            QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import os
 
#  # 한글 폰트 적용        
# path = 'C:/Windows/Fonts/malgun.ttf'
# font_name = fm.FontProperties(fname=path, size=12).get_name()
# plt.rc('font', family=font_name)
 
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
class myWindow(QWidget):
 
    def __init__(self):
        super().__init__()
        self.resize(500,600) # 위젯 사이즈 
         
        # List for Pandas Dataframes
        self.df_list = []
         
        self.cmb = QComboBox(self)
        open_btn = QPushButton('open excel file', self)
        chart_btn = QPushButton('visulaize', self)
         
        # 수평 박스 배치
        hbox = QHBoxLayout()
        hbox.addWidget(self.cmb)
        hbox.addWidget(open_btn)
        hbox.addWidget(chart_btn)
 
        self.table = QTableWidget(self)
 
        # 수직 박스 배치
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.table)
        self.setLayout(vbox)
 
        # 시그널 연결
        open_btn.clicked.connect(self.clickOpenBtn)
        chart_btn.clicked.connect(self.clickChartBtn)
        self.cmb.currentIndexChanged[int].connect(self.cmbChanged)        
 
    def clickOpenBtn(self):
        file_path, ext = QFileDialog.getOpenFileName(self, 'open file', os.getcwd(), 'excel file (*.xls *.xlsx)')
        if file_path:
            self.df_list = self.loadData(file_path)
 
            # 콤보박스 워크시트 목록 추가
            for i in self.df_list:
                self.cmb.addItem(i.name)
 
            self.initTableWidget(0)            
 
    def clickChartBtn(self):
        # 현재 선택된 Dataframe id
        id = self.cmb.currentIndex()
        name = self.cmb.currentText()
        if id>-1:
            df = self.df_list[id].copy()      
            if not df.empty:                
                df.set_index(df.columns[0], drop=True, inplace=True)                                
                df.plot()                
                plt.title(f'기상청 날씨-{name}')                
                plt.show()
 
    def cmbChanged(self, id):
        self.initTableWidget(id)
 
    def loadData(self, file_name):
        df_list = []        
        with pd.ExcelFile(file_name) as wb:            
            for i, sn in enumerate(wb.sheet_names):              
                try:
                    df = pd.read_excel(wb, sheet_name=sn)
                except Exception as e:
                    print('File read error:', e)
                else:
                    df = df.fillna(0)
                    df.name = sn
                    df_list.append(df)
        return df_list
 
    def initTableWidget(self, id):
        # 테이블 위젯 값 쓰기
        self.table.clear()
        # select dataframe
        df = self.df_list[id];        
        # table write        
        col = len(df.keys())
        self.table.setColumnCount(col)
        self.table.setHorizontalHeaderLabels(df.keys())
 
        row = len(df.index)
        self.table.setRowCount(row)
        self.writeTableWidget(id, df, row, col)      
 
    def writeTableWidget(self, id, df, row, col):
        for r in range(row):
            for c in range(col):
                item = QTableWidgetItem(str(df.iloc[r][c]))
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = myWindow()
    w.show()
    sys.exit(app.exec_())