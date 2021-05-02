from PyQt5.QtWidgets import *
from PyQt5.Qt import *

from .user_interrupt_labelling_exception import UserInterruptLabellingException

class LabellingDialogBox(QDialog):
    def __init__(self, type, number, total, row_A, row_B, column_names):
        QDialog.__init__(self)

        self.setWindowTitle("FALSE " + type + " couple " + str(number) + "/" + str(total))
        self.setMinimumSize(600, 300)
        self.setSizeGripEnabled(True)

        layout = QFormLayout()
        layout.addRow(QLabel("The system predicted that this pair is a FALSE " + type + " :"))
        layout.addRow(self.__table_widget(row_A, row_B, column_names))
        layout.addRow(QLabel("It is a match or a not match?"))
        layout.addRow(self.__buttons_widget())

        self.setLayout(layout)

    def __table_widget(self, row_A, row_B, column_names):       
        column_names.pop(0)

        tableWidget = QTableWidget(2, len(column_names))
        
        tableWidget.setHorizontalHeaderLabels(column_names)
        tableWidget.verticalHeader().hide()

        tableWidget.horizontalHeader().setStretchLastSection(True)

        for i in range(len(column_names)):
            row_A_table_widget_item = QTableWidgetItem(str(row_A[column_names[i]].values[0]))
            row_A_table_widget_item.setFlags(row_A_table_widget_item.flags() & (~ Qt.ItemIsEditable))
            
            tableWidget.setItem(0, i, row_A_table_widget_item)

            row_B_table_widget_item = QTableWidgetItem(str(row_B[column_names[i]].values[0]))
            row_B_table_widget_item.setFlags(row_B_table_widget_item.flags() & (~ Qt.ItemIsEditable))

            tableWidget.setItem(1, i, row_B_table_widget_item)

        tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        return tableWidget

    def __buttons_widget(self):
        def __match():
            self.accept()
        def __not_match():
            self.reject()
            
        widget = QWidget()
        layout = QHBoxLayout()

        match_button = QPushButton("Match")
        match_button.setFixedWidth(250)
        match_button.clicked.connect(__match)

        not_match_button = QPushButton("Not match")
        not_match_button.setFixedWidth(250)
        not_match_button.clicked.connect(__not_match)

        layout.addWidget(match_button)
        layout.addWidget(not_match_button)

        widget.setLayout(layout)

        return widget

    def keyPressEvent(self, event):
        return

    def closeEvent(self, event):
        mesassage_box_value = QMessageBox.warning(self, "Warning", "If you close the labelling window the process will be stopped. Are you sure?", 
                                                  QMessageBox.Yes, QMessageBox.No)

        if mesassage_box_value == QMessageBox.Yes:
            self.setResult(2)
            event.accept()
        else:
            event.ignore()