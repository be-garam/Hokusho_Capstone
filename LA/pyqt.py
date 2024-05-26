import sys
import pandas as pd
from PySide6.QtWidgets import *

class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        '''Blank Table Widget'''
        table_widget = QTableWidget()

        '''PushButton for Load CSV file'''
        button_load = QPushButton("Load")
        button_load.clicked.connect(lambda state, widget = table_widget: self.slot_button_load(state, widget))

        '''PushButton for Save modified CSV'''
        button_save = QPushButton("Save")
        button_save.clicked.connect(lambda state, widget = table_widget: self.slot_button_save(state, widget))

        layout.addWidget(table_widget)
        layout.addWidget(button_load)
        layout.addWidget(button_save)

        self.setLayout(layout)
        self.resize(500, 500)
        self.show()


    def slot_button_load(self, state, widget):
        filename = QFileDialog.getOpenFileName(self, 'Open file', './')

        if filename[0]:
            df = pd.read_csv(filename[0], index_col = 0)
            self.create_table_widget(widget, df)


    def create_table_widget(self, widget, df):
        widget.setRowCount(len(df.index))
        widget.setColumnCount(len(df.columns))
        widget.setHorizontalHeaderLabels(df.columns)
        widget.setVerticalHeaderLabels(df.index)

        for row_index, row in enumerate(df.index):
            for col_index, column in enumerate(df.columns):
                value = df.loc[row][column]
                item = QTableWidgetItem(str(value))
                widget.setItem(row_index, col_index, item)


    def slot_button_save(self, state, widget):
        for row_index in range(widget.rowCount()):
            for col_index in range(widget.columnCount()):
                item = widget.item(row_index, col_index)
                content = item.text()
                print(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())