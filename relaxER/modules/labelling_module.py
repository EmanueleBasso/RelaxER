import sys
from PyQt5.QtWidgets import QApplication

from ..utils import read_dataset

from ..gui.user_interrupt_labelling_exception import UserInterruptLabellingException
from ..gui.labelling_dialog import LabellingDialogBox

class LabellingModule:
    def __init__(self, read_oracle, oracle_files, directory_path, labelling_ui):
        self.__read_oracle = read_oracle

        if read_oracle:
            self.__oracle_dataframes = list()

            for oracle_file in oracle_files:
                self.__oracle_dataframes.append(read_dataset(directory_path, oracle_file))

        self.__labelling_ui = labelling_ui

        self.__real_fp = 0
        self.__real_fn = 0

    def label(self, examples_pos, examples_neg, labelled_pair, unlabelled_pair, column_names, verbose):
        if self.__read_oracle:
            self.__check_oracle(examples_pos, labelled_pair, unlabelled_pair, column_names, 0)
            self.__check_oracle(examples_neg, labelled_pair, unlabelled_pair, column_names, 1)
        else:
            if self.__labelling_ui == False:
                self.__show_examples_prompt(examples_pos, labelled_pair, unlabelled_pair, column_names, 0)
                self.__show_examples_prompt(examples_neg, labelled_pair, unlabelled_pair, column_names, 1)
            else:
                app = QApplication(sys.argv)
                
                self.__show_examples_gui(examples_pos, labelled_pair, unlabelled_pair, column_names, 0)
                self.__show_examples_gui(examples_neg, labelled_pair, unlabelled_pair, column_names, 1)

        if verbose:
            print("\n" + "Real False Positive: " + str(self.__real_fp))
            print("Real False Negative: " + str(self.__real_fn) + "\n")

    def __check_oracle(self, examples, labelled_pair, unlabelled_pair, column_names, prediction):
        for example in examples:
            id_A = example["id_A"]
            id_B = example["id_B"]

            found = False

            for oracle_dataframe in self.__oracle_dataframes:
                result = self.__check_dataframe(id_A, id_B, oracle_dataframe)

                if result:
                    self.__match(id_A, id_B, labelled_pair, unlabelled_pair, 1, column_names, prediction)
                    found = True
                    break

            if not found:
                self.__match(id_A, id_B, labelled_pair, unlabelled_pair, 0, column_names, prediction)

    def __check_dataframe(self, id_A, id_B, dataframe):
        for index, row in dataframe.iterrows():
            if (row["ltable_id"] == id_A) and (row["rtable_id"] == id_B):
                if row["label"] == 1:
                    return True
                else:
                    return False

        return False

    def __show_examples_prompt(self, examples, labelled_pair, unlabelled_pair, column_names, prediction):
        iteration_count = 1

        for example in examples:
            id_A = example["id_A"]
            id_B = example["id_B"]

            row_A = unlabelled_pair.dataframe_A[unlabelled_pair.dataframe_A["id"]  == id_A]
            row_B = unlabelled_pair.dataframe_B[unlabelled_pair.dataframe_B["id"]  == id_B]

            if prediction == 0:
                print("\n" + "FALSE POSITIVE couple " + str(iteration_count) + "/" + str(len(examples)) + ":")
            elif prediction == 1:
                print("\n" + "FALSE NEGATIVE couple " + str(iteration_count) + "/" + str(len(examples)) + ":")

            for column_name in column_names:
                if column_name == "id":
                    continue
                
                print("Attribute '" + column_name + "':")
                print("\t" + "Row A: " + str(row_A[column_name].values[0]))
                print("\t" + "Row B: " + str(row_B[column_name].values[0]))
                print()

            if prediction == 0:
                print("The system predicted that this pair is a FALSE POSITIVE.")
            elif prediction == 1:
                print("The system predicted that this pair is a FALSE NEGATIVE.")

            wrong_answer = True

            while wrong_answer:
                result = input("It is a match (1) or a not match (0): ")

                if (result == "0") or (result == "1"):
                    result = int(result)

                    self.__match(id_A, id_B, labelled_pair, unlabelled_pair, result, column_names, prediction)

                    wrong_answer = False
                else:
                    print("\n" + "Error, allowed values ​​are 0 or 1." + "\n")

            iteration_count = iteration_count + 1

    def __show_examples_gui(self, examples, labelled_pair, unlabelled_pair, column_names, prediction):
        iteration_count = 1

        for example in examples:
            id_A = example["id_A"]
            id_B = example["id_B"]

            row_A = unlabelled_pair.dataframe_A[unlabelled_pair.dataframe_A["id"]  == id_A]
            row_B = unlabelled_pair.dataframe_B[unlabelled_pair.dataframe_B["id"]  == id_B]

            self.__labelling_dialog_box = None

            if prediction == 0:
                self.__labelling_dialog_box = LabellingDialogBox("POSITIVE", iteration_count, len(examples), row_A, 
                                                                 row_B, column_names.tolist())
            elif prediction == 1:
                self.__labelling_dialog_box = LabellingDialogBox("NEGATIVE", iteration_count, len(examples), row_A, 
                                                                 row_B, column_names.tolist())

            result = self.__labelling_dialog_box.exec()

            if result == 2:
                raise UserInterruptLabellingException("Labelling interrupted")

            self.__match(id_A, id_B, labelled_pair, unlabelled_pair, result, column_names, prediction)

            iteration_count = iteration_count + 1

    def __match(self, id_A, id_B, labelled_pair, unlabelled_pair, label, column_names, prediction):
        labelled_pair.add_labelled_pair(id_A, id_B, label, column_names)
        unlabelled_pair.remove_pair(id_A, id_B)

        if label == prediction:
            if label == 1:
                self.__real_fn += 1
            else:
                self.__real_fp += 1