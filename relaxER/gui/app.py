import sys
import os
import signal
import platform

from PyQt5.QtWidgets import *
from PyQt5.Qt import QPixmap, QBrush

from multiprocessing import Process, Queue, Event, set_start_method

from .subprocesses import run_discovery, run_eval, run_prediction
from .thread_listener import ThreadListener

from ..model.rule_repository import RuleRepository

class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        set_start_method("spawn", force=True)

        self.__directory_path = ""
        self.__first_table = "tableA.csv"
        self.__second_table = "tableB.csv"
        self.__initial_pair = "initialPair.csv"
        self.__active_learning = True
        self.__threshold_base = "0.7"
        self.__min_meaningfulness = "0.45"
        self.__degradation = "20"
        self.__one_predicate_min_threshold = "0.85"
        self.__min_reduction_dataset = "1"
        self.__iteration = "5"
        self.__number_examples_iter = "10"
        self.__delta = "0.05"
        self.__alpha = "10"
        self.__random_start = False
        self.__number_tuple_pick = "30"
        self.__frac_zero_pick = "25"
        self.__read_oracle = False
        self.__oracle_files = "train.csv, test.csv, valid.csv"
        self.__test = "test.csv"
        self.__first_table_predict = "tableA.csv"
        self.__second_table_predict = "tableB.csv"
        self.__output_file_name = "prediction.csv"

        self.__rule_repository = None

        self.setUI()

    def setUI(self):
        self.__window = QMainWindow()
        self.__window.resize(900, 300)
        self.__window.setWindowTitle("RelaxER")
        
        self.__add_menu_bar()

        self.__window_widget = QTabWidget(self.__window)
        self.__window.setCentralWidget(self.__window_widget)

        first_tab_layout = QFormLayout()
        first_tab_layout.addRow(self.__directory_path_widget())
        first_tab_layout.addRow(self.__files_widget())
        first_tab_layout.addRow(self.__parameters_random_start_widget())
        first_tab_layout.addRow(self.__parameters_widget())
        first_tab_layout.addRow(self.__parameters_active_learning_widget())
        first_tab_layout.addRow(self.__run_button())

        first_tab_widget = QWidget()
        first_tab_widget.setLayout(first_tab_layout)

        self.__window_widget.addTab(first_tab_widget, "Discovery")

        second_tab_layout = QFormLayout()
        second_tab_layout.addRow(self.__rule_repository_widget())
        second_tab_layout.addRow(self.__eval_test_set_widget())
        second_tab_layout.addRow(self.__predict_match_widget())
        
        second_tab_widget = QWidget()
        second_tab_widget.setLayout(second_tab_layout)

        self.__window_widget.addTab(second_tab_widget, "Result")
        self.__window_widget.setTabEnabled(1, False)

    def start(self):
        self.__window.show()
        res = self.exec_()

        try:
            self.__thread_listener.abort = True

            if platform.system == "Windows":
                os.kill(self.__background_process.pid, signal.CTRL_C_EVENT)
            else:
                os.kill(self.__background_process.pid, signal.SIGINT)
            
            self.__background_process.join()
        except AttributeError:
            pass
        finally:
            sys.exit(res)

    def __add_menu_bar(self):
        def __import():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", os.getcwd(), filter="*.pickle")

            if value[0]:
                res = RuleRepository.import_rules(value[0])

                if res == None:
                    mesassage_box = QMessageBox.critical(self.__window, "Error", "Could not load the model", QMessageBox.Ok)
                else:
                    self.__rule_repository = res

                    self.__text_edit_rule_repository.setText(str(self.__rule_repository))

                    self.__window_widget.setTabEnabled(1, True)
                    self.__export_action.setEnabled(True)

                    mesassage_box = QMessageBox.information(self.__window, "Success", "Model loaded correctly", QMessageBox.Ok)

        def __export():
            value = QFileDialog.getSaveFileName(self.__window, "Save model", os.getcwd(), filter="*.pickle")

            if value[0]:
                path = value[0]
                file_name = os.path.basename(value[0])

                if ".pickle" not in file_name:
                    path = path + ".pickle"

                if self.__rule_repository.export_rules(path) == None:
                    mesassage_box = QMessageBox.critical(self.__window, "Error", "Could not save the model", QMessageBox.Ok)
                else:
                    mesassage_box = QMessageBox.information(self.__window, "Success", "Model saved correctly", QMessageBox.Ok)

        def __exit():
            self.__window.close()

        menu_bar = self.__window.menuBar()

        file_menu = menu_bar.addMenu("File")

        self.__import_action = QAction("Import model", self.__window)
        self.__import_action.setEnabled(False)
        self.__import_action.triggered.connect(__import)
        file_menu.addAction(self.__import_action)

        self.__export_action = QAction("Export model", self.__window)
        self.__export_action.setEnabled(False)
        self.__export_action.triggered.connect(__export)
        file_menu.addAction(self.__export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self.__window)
        exit_action.triggered.connect(__exit)
        file_menu.addAction(exit_action)

    def __directory_path_widget(self):
        def __choose_directory_path():
            path = ""
            if self.__directory_path:
                path = self.__directory_path
            else:
                path = os.getcwd()

            value = QFileDialog.getExistingDirectory(self.__window, "Choose directory", path)

            if value:
                button.setText(value)
                self.__directory_path = value

                self.__form_group_box_files.setEnabled(True)
                self.__form_group_box_parameters.setEnabled(True)
                self.__form_group_box_parameters_random_start.setEnabled(True)
                self.__form_group_box_parameters_oracle.setEnabled(True)
                self.__form_group_box_parameters_active_learning.setEnabled(True)
                self.__run_button.setEnabled(True)

                self.__import_action.setEnabled(True)

        button = QPushButton("Choose directory", self.__window)
        button.clicked.connect(__choose_directory_path)

        layout = QFormLayout()
        layout.addRow(QLabel("Directory path:"), button)

        self.__widget_directory_path = QWidget()
        self.__widget_directory_path.setLayout(layout)

        return self.__widget_directory_path

    def __files_widget(self):
        def __choose_first_file():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_first_table.setText(file_name)
                self.__first_table = file_name

        def __choose_second_file():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_second_table.setText(file_name)
                self.__second_table = file_name

        def __choose_initial_pairs():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_initial_pairs.setText(file_name)
                self.__initial_pair = file_name

        button_first_table = QPushButton(self.__first_table, self.__window)
        button_first_table.clicked.connect(__choose_first_file)

        button_second_table = QPushButton(self.__second_table, self.__window)
        button_second_table.clicked.connect(__choose_second_file)

        button_initial_pairs = QPushButton(self.__initial_pair, self.__window)
        button_initial_pairs.clicked.connect(__choose_initial_pairs)

        layout = QGridLayout()

        layout.addWidget(QLabel("First table:"), 0, 0)
        layout.addWidget(button_first_table, 0, 1)
        layout.addWidget(QLabel("Second table:"), 0, 2)
        layout.addWidget(button_second_table, 0, 3)

        layout.addWidget(QLabel("Initial pairs:"), 1, 0)
        layout.addWidget(button_initial_pairs, 1, 1)

        self.__form_group_box_files = QGroupBox("Files  ")
        self.__form_group_box_files.setLayout(layout)
        self.__form_group_box_files.setEnabled(False)

        return self.__form_group_box_files

    def __parameters_widget(self):
        self.__line_edit_threshold_base = QLineEdit(self.__window)
        self.__line_edit_threshold_base.setText(self.__threshold_base)

        self.__line_edit_min_meaningfulness = QLineEdit(self.__window)
        self.__line_edit_min_meaningfulness.setText(self.__min_meaningfulness)

        self.__line_edit_degradation = QLineEdit(self.__window)
        self.__line_edit_degradation.setText(self.__degradation)

        self.__line_edit_one_predicate_min_threshold = QLineEdit(self.__window)
        self.__line_edit_one_predicate_min_threshold.setText(self.__one_predicate_min_threshold)

        self.__line_edit_min_reduction_dataset = QLineEdit(self.__window)
        self.__line_edit_min_reduction_dataset.setText(self.__min_reduction_dataset)

        layout = QGridLayout()

        layout.addWidget(QLabel("Threshold base:"), 0, 0)
        layout.addWidget(self.__line_edit_threshold_base, 0, 1)
        layout.addWidget(QLabel("Minimum meaningfulness:"), 0, 2)
        layout.addWidget(self.__line_edit_min_meaningfulness, 0, 3)

        layout.addWidget(QLabel("Degradation (%):"), 1, 0)
        layout.addWidget(self.__line_edit_degradation, 1, 1)
        layout.addWidget(QLabel("One predicate minimum threshold:"), 1, 2)
        layout.addWidget(self.__line_edit_one_predicate_min_threshold, 1, 3)

        layout.addWidget(QLabel("Minimum reduction dataset (%):"), 2, 0)
        layout.addWidget(self.__line_edit_min_reduction_dataset, 2, 1)

        self.__form_group_box_parameters = QGroupBox("Generation parameters  ")
        self.__form_group_box_parameters.setLayout(layout)
        self.__form_group_box_parameters.setEnabled(False)

        return self.__form_group_box_parameters

    def __parameters_random_start_widget(self):
        self.__line_edit_number_tuple_pick = QLineEdit(self.__window)
        self.__line_edit_number_tuple_pick.setText(self.__number_tuple_pick)

        self.__line_edit_frac_zero_pick = QLineEdit(self.__window)
        self.__line_edit_frac_zero_pick.setText(self.__frac_zero_pick)

        layout = QGridLayout()

        layout.addWidget(QLabel("Number tuples to pick:"), 0, 0)
        layout.addWidget(self.__line_edit_number_tuple_pick, 0, 1)
        layout.addWidget(QLabel("Percentage of 0 to pick (%):"), 0, 2)
        layout.addWidget(self.__line_edit_frac_zero_pick, 0, 3)

        self.__form_group_box_parameters_random_start = QGroupBox("Random start  ")
        self.__form_group_box_parameters_random_start.setCheckable(True)
        self.__form_group_box_parameters_random_start.setChecked(False)
        self.__form_group_box_parameters_random_start.setLayout(layout)
        self.__form_group_box_parameters_random_start.setEnabled(False)

        return self.__form_group_box_parameters_random_start

    def __parameters_oracle_widget(self):
        self.__line_edit_oracle_files = QLineEdit(self.__window)
        self.__line_edit_oracle_files.setText(self.__oracle_files)

        layout = QGridLayout()

        layout.addWidget(QLabel("Oracle files (separated by commas):"), 0, 0)
        layout.addWidget(self.__line_edit_oracle_files, 0, 1)

        self.__form_group_box_parameters_oracle = QGroupBox("Read from oracle files  ")
        self.__form_group_box_parameters_oracle.setCheckable(True)
        self.__form_group_box_parameters_oracle.setChecked(False)
        self.__form_group_box_parameters_oracle.setLayout(layout)
        self.__form_group_box_parameters_oracle.setEnabled(False)

        return self.__form_group_box_parameters_oracle

    def __parameters_active_learning_widget(self):
        self.__line_edit_iteration = QLineEdit(self.__window)
        self.__line_edit_iteration.setText(self.__iteration)

        self.__line_edit_number_examples_iter = QLineEdit(self.__window)
        self.__line_edit_number_examples_iter.setText(self.__number_examples_iter)

        self.__line_edit_delta = QLineEdit(self.__window)
        self.__line_edit_delta.setText(self.__delta)

        self.__line_edit_one_alpha = QLineEdit(self.__window)
        self.__line_edit_one_alpha.setText(self.__alpha)

        layout = QGridLayout()

        layout.addWidget(QLabel("Number iteration:"), 0, 0)
        layout.addWidget(self.__line_edit_iteration, 0, 1)
        layout.addWidget(QLabel("Number examples iteration:"), 0, 2)
        layout.addWidget(self.__line_edit_number_examples_iter, 0, 3)

        layout.addWidget(QLabel("Delta:"), 1, 0)
        layout.addWidget(self.__line_edit_delta, 1, 1)
        layout.addWidget(QLabel("Alpha (%):"), 1, 2)
        layout.addWidget(self.__line_edit_one_alpha, 1, 3)

        layout.addWidget(self.__parameters_oracle_widget(), 2, 0, 1, 4)

        self.__form_group_box_parameters_active_learning = QGroupBox("Active Learning  ")
        self.__form_group_box_parameters_active_learning.setCheckable(True)
        self.__form_group_box_parameters_active_learning.setLayout(layout)
        self.__form_group_box_parameters_active_learning.setEnabled(False)

        return self.__form_group_box_parameters_active_learning

    def __run_button(self):
        def __run_finished():
            res = self.__queue.get()

            if res == "Stopped":
                print("===> Discovery Stopped")

                self.__rule_repository = None
            elif isinstance(res, Exception):
                print("===> Discovery Error")

                mesassage_box = QMessageBox.critical(self.__window, "Error", str(res), QMessageBox.Ok)

                self.__rule_repository = None
            else:
                print("===> Discovery Ended")

                self.__rule_repository = res
            
                self.__text_edit_rule_repository.setText(str(self.__rule_repository))

                self.__window_widget.setTabEnabled(1, True)
                self.__window_widget.setCurrentIndex(1)
                self.__import_action.setEnabled(True)
                self.__export_action.setEnabled(True)

            self.__run_button.setText("Run")
            self.__run_button.clicked.disconnect(__stop)
            self.__run_button.clicked.connect(__run)

            self.__widget_directory_path.setEnabled(True)
            self.__form_group_box_files.setEnabled(True)
            self.__form_group_box_parameters.setEnabled(True)
            self.__form_group_box_parameters_random_start.setEnabled(True)
            self.__form_group_box_parameters_oracle.setEnabled(True)
            self.__form_group_box_parameters_active_learning.setEnabled(True)

        def __run():
            self.__active_learning = self.__form_group_box_parameters_active_learning.isChecked()
            self.__random_start = self.__form_group_box_parameters_random_start.isChecked()
            self.__read_oracle = self.__form_group_box_parameters_oracle.isChecked()

            self.__widget_directory_path.setEnabled(False)
            self.__form_group_box_files.setEnabled(False)
            self.__form_group_box_parameters.setEnabled(False)
            self.__form_group_box_parameters_random_start.setEnabled(False)
            self.__form_group_box_parameters_oracle.setEnabled(False)
            self.__form_group_box_parameters_active_learning.setEnabled(False)
            self.__window_widget.setTabEnabled(1, False)
            self.__import_action.setEnabled(False)
            self.__export_action.setEnabled(False)

            self.__precision_label.setText("-")
            self.__recall_label.setText("-")
            self.__fmeasure_label.setText("-")

            self.__event = Event()
            self.__queue = Queue()

            self.__background_process = Process(target=run_discovery, args=(self.__queue,
                                                                            self.__event,
                                                                            self.__directory_path,
                                                                            self.__first_table,
                                                                            self.__second_table,
                                                                            self.__initial_pair,
                                                                            self.__active_learning,
                                                                            float(self.__line_edit_threshold_base.text()),
                                                                            float(self.__line_edit_min_meaningfulness.text()),
                                                                            int(self.__line_edit_degradation.text()),
                                                                            float(self.__line_edit_one_predicate_min_threshold.text()),
                                                                            int(self.__line_edit_min_reduction_dataset.text()),
                                                                            int(self.__line_edit_iteration.text()),
                                                                            int(self.__line_edit_number_examples_iter.text()),
                                                                            float(self.__line_edit_delta.text()),
                                                                            int(self.__line_edit_one_alpha.text()),
                                                                            self.__random_start,
                                                                            int(self.__line_edit_number_tuple_pick.text()),
                                                                            float(self.__line_edit_frac_zero_pick.text()),
                                                                            self.__read_oracle,
                                                                            self.__line_edit_oracle_files.text()
                                                                        )
                                            )

            self.__thread_listener = ThreadListener(self.__event)
            self.__thread_listener.finished.connect(__run_finished)

            self.__background_process.start()
            self.__thread_listener.start()

            print("===> Discovery Started")

            self.__run_button.setText("Stop")
            self.__run_button.clicked.disconnect(__run)
            self.__run_button.clicked.connect(__stop)

        def __stop():
            self.__queue.put("Stopped")
            self.__thread_listener.abort = True

            if platform.system == "Windows":
                os.kill(self.__background_process.pid, signal.CTRL_C_EVENT)
            else:
                os.kill(self.__background_process.pid, signal.SIGINT)
            
            self.__background_process.join()

        self.__run_button = QPushButton("Run", self.__window)
        self.__run_button.clicked.connect(__run)
        self.__run_button.setEnabled(False)

        return self.__run_button

    def __rule_repository_widget(self):
        self.__text_edit_rule_repository = QTextEdit()
        self.__text_edit_rule_repository.setReadOnly(True)

        return self.__text_edit_rule_repository

    def __eval_test_set_widget(self):
        def __clicked():
            if self.__form_group_box_predict_match.isChecked() == False:
                self.__form_group_box_eval_test_set.setChecked(True)
            elif self.__form_group_box_eval_test_set.isChecked() == True:
                self.__form_group_box_predict_match.setChecked(False)
            else:
                self.__form_group_box_predict_match.setChecked(True)

        def __choose_test_file():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_test_file.setText(file_name)
                self.__test = file_name
        
        def __run_finished():
            res = self.__queue.get()

            if res == "Stopped":
                print("===> Evaluation Stopped")
            elif isinstance(res, Exception):
                print("===> Evaluation Error")

                mesassage_box = QMessageBox.critical(self.__window, "Error", str(res), QMessageBox.Ok)
            else:
                print("===> Evaluation Ended")

                self.__precision_label.setText(str(round(res, 2)))
                self.__recall_label.setText(str(round(self.__queue.get(), 2)))
                self.__fmeasure_label.setText(str(round(self.__queue.get(), 2)))

            button_run_eval.setText("Run")
            button_run_eval.clicked.disconnect(__stop)
            button_run_eval.clicked.connect(__run)

            self.__window_widget.setTabEnabled(0, True)
            button_test_file.setEnabled(True)
            self.__form_group_box_predict_match.setEnabled(True)
            self.__import_action.setEnabled(True)
            self.__export_action.setEnabled(True)

        def __run():
            self.__precision_label.setText("-")
            self.__recall_label.setText("-")
            self.__fmeasure_label.setText("-")

            self.__window_widget.setTabEnabled(0, False)
            button_test_file.setEnabled(False)
            self.__form_group_box_predict_match.setEnabled(False)
            self.__import_action.setEnabled(False)
            self.__export_action.setEnabled(False)

            self.__event = Event()
            self.__queue = Queue()

            self.__background_process = Process(target=run_eval, args=(self.__queue,
                                                                    self.__event,
                                                                    self.__rule_repository,
                                                                    self.__directory_path,
                                                                    self.__first_table,
                                                                    self.__second_table,
                                                                    self.__test
                                                                )
                                            )
            
            self.__thread_listener = ThreadListener(self.__event)
            self.__thread_listener.finished.connect(__run_finished)

            self.__background_process.start()
            self.__thread_listener.start()

            print("===> Evaluation Started")

            button_run_eval.setText("Stop")
            button_run_eval.clicked.disconnect(__run)
            button_run_eval.clicked.connect(__stop)

        def __stop():
            self.__queue.put("Stopped")
            self.__thread_listener.abort = True

            if platform.system == "Windows":
                os.kill(self.__background_process.pid, signal.CTRL_C_EVENT)
            else:
                os.kill(self.__background_process.pid, signal.SIGINT)
            
            self.__background_process.join()

        button_test_file = QPushButton(self.__test, self.__window)
        button_test_file.clicked.connect(__choose_test_file)

        button_run_eval = QPushButton("Run", self.__window)
        button_run_eval.clicked.connect(__run)

        self.__precision_label = QLabel("-")
        self.__recall_label = QLabel("-")
        self.__fmeasure_label = QLabel("-")

        layout = QGridLayout()
        layout.addWidget(QLabel("Test set:"), 0, 0)
        layout.addWidget(button_test_file, 0, 1)

        layout.addWidget(button_run_eval, 1, 0, 1, 4)

        layout.addWidget(QLabel("Precision:"), 2, 0)
        layout.addWidget(self.__precision_label, 2, 1)

        layout.addWidget(QLabel("Recall:"), 3, 0)
        layout.addWidget(self.__recall_label, 3, 1)

        layout.addWidget(QLabel("F-measure:"), 4, 0)
        layout.addWidget(self.__fmeasure_label, 4, 1)

        self.__form_group_box_eval_test_set = QGroupBoxRadio("Evaluate on Test Set  ")
        self.__form_group_box_eval_test_set.setCheckable(True)
        self.__form_group_box_eval_test_set.clicked.connect(__clicked)

        self.__form_group_box_eval_test_set.setLayout(layout)

        return self.__form_group_box_eval_test_set

    def __predict_match_widget(self):
        def __clicked():
            if self.__form_group_box_eval_test_set.isChecked() == False:
                self.__form_group_box_predict_match.setChecked(True)
            elif self.__form_group_box_predict_match.isChecked() == True:
                self.__form_group_box_eval_test_set.setChecked(False)
            else:
                self.__form_group_box_eval_test_set.setChecked(True)

        def __choose_first_file():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_first_table.setText(file_name)
                self.__first_table_predict = file_name

        def __choose_second_file():
            value = QFileDialog.getOpenFileName(self.__window, "Choose file", self.__directory_path, filter="*.csv")

            if value[0]:
                file_name = os.path.basename(value[0])

                button_second_table.setText(file_name)
                self.__second_table_predict = file_name

        def __run_finished():
            res = self.__queue.get()

            if res == "Stopped":
                print("===> Prediction Stopped")
            elif isinstance(res, Exception):
                print("===> Prediction Error")

                mesassage_box = QMessageBox.critical(self.__window, "Error", str(res), QMessageBox.Ok)
            else:
                print("===> Prediction Ended")

                mesassage_box = QMessageBox.information(self.__window, "Success", "Created the " + self.__output_file_name + " file with the predictions", QMessageBox.Ok)

            button_run_predict.setText("Run")
            button_run_predict.clicked.disconnect(__stop)
            button_run_predict.clicked.connect(__run)

            self.__window_widget.setTabEnabled(0, True)
            button_first_table.setEnabled(True)
            button_second_table.setEnabled(True)
            self.__line_edit_output_file_name.setEnabled(True)
            self.__form_group_box_eval_test_set.setEnabled(True)
            self.__import_action.setEnabled(True)
            self.__export_action.setEnabled(True)

        def __run():
            self.__window_widget.setTabEnabled(0, False)
            button_first_table.setEnabled(False)
            button_second_table.setEnabled(False)
            self.__line_edit_output_file_name.setEnabled(False)
            self.__form_group_box_eval_test_set.setEnabled(False)
            self.__import_action.setEnabled(False)
            self.__export_action.setEnabled(False)

            self.__event = Event()
            self.__queue = Queue()

            self.__background_process = Process(target=run_prediction, args=(self.__queue,
                                                                    self.__event,
                                                                    self.__rule_repository,
                                                                    self.__directory_path,
                                                                    self.__first_table_predict,
                                                                    self.__second_table_predict,
                                                                    self.__output_file_name
                                                                )
                                            )
            
            self.__thread_listener = ThreadListener(self.__event)
            self.__thread_listener.finished.connect(__run_finished)

            self.__background_process.start()
            self.__thread_listener.start()

            print("===> Prediction Started")

            button_run_predict.setText("Stop")
            button_run_predict.clicked.disconnect(__run)
            button_run_predict.clicked.connect(__stop)

        def __stop():
            self.__queue.put("Stopped")
            self.__thread_listener.abort = True
            
            if platform.system == "Windows":
                os.kill(self.__background_process.pid, signal.CTRL_C_EVENT)
            else:
                os.kill(self.__background_process.pid, signal.SIGINT)
            
            self.__background_process.join()

        button_first_table = QPushButton(self.__first_table_predict, self.__window)
        button_first_table.clicked.connect(__choose_first_file)

        button_second_table = QPushButton(self.__second_table_predict, self.__window)
        button_second_table.clicked.connect(__choose_second_file)

        self.__line_edit_output_file_name = QLineEdit(self.__window)
        self.__line_edit_output_file_name.setText(self.__output_file_name)

        button_run_predict = QPushButton("Run", self.__window)
        button_run_predict.clicked.connect(__run)

        layout = QGridLayout()

        layout.addWidget(QLabel("First table:"), 0, 0)
        layout.addWidget(button_first_table, 0, 1)
        layout.addWidget(QLabel("Second table:"), 0, 2)
        layout.addWidget(button_second_table, 0, 3)

        layout.addWidget(QLabel("Output file name:"), 1, 0)
        layout.addWidget(self.__line_edit_output_file_name, 1, 1, 1, 3)

        layout.addWidget(button_run_predict, 2, 0, 1, 4)
        
        self.__form_group_box_predict_match = QGroupBoxRadio("Predict Match  ")
        self.__form_group_box_predict_match.setCheckable(True)
        self.__form_group_box_predict_match.setChecked(False)
        self.__form_group_box_predict_match.clicked.connect(__clicked)

        self.__form_group_box_predict_match.setLayout(layout)

        return self.__form_group_box_predict_match

class QGroupBoxRadio(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

    def paintEvent(self, event):
        paint = QStylePainter(self)
        option = QStyleOptionGroupBox()

        self.initStyleOption(option)
        paint.drawComplexControl(QStyle.CC_GroupBox, option)

        option.rect = self.style().subControlRect(QStyle.CC_GroupBox, option, QStyle.SC_GroupBoxCheckBox, self)

        paint.save()
        px = QPixmap(option.rect.width(), option.rect.height())
        px.fill()
        brush = QBrush(px)
        paint.fillRect(option.rect, brush)
        paint.restore()
        
        paint.drawPrimitive(QStyle.PE_IndicatorRadioButton, option)