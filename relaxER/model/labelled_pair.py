import pandas

class LabelledPair:
    def __init__(self, dataframe_A, dataframe_B):
        self.pairs = None
        self.dataframe_A = dataframe_A
        self.dataframe_A.set_index("id", drop=False, inplace=True)
        self.dataframe_B = dataframe_B
        self.dataframe_B.set_index("id", drop=False, inplace=True)
        
    def initial_labelled_pairs(self, initial_pair):
        column_names = []

        for col in self.dataframe_A.columns:
            column_names.append(col + "_A")
        
        for col in self.dataframe_B.columns:
            column_names.append(col + "_B")

        column_names.append("label")

        labelled_pairs = pandas.DataFrame(columns=column_names)

        for index, row in initial_pair.iterrows():
            ltable_id = row["ltable_id"]
            rtable_id = row["rtable_id"]
            label = row["label"]

            ltable_row = self.dataframe_A.loc[self.dataframe_A["id"] == ltable_id]
            rtable_row = self.dataframe_B.loc[self.dataframe_B["id"] == rtable_id]

            new_tuple = {}

            for col in self.dataframe_A.columns:
                new_tuple[col + "_A"] = ltable_row[col].values[0]

            for col in self.dataframe_B.columns:
                new_tuple[col + "_B"] = rtable_row[col].values[0]
            
            new_tuple["label"] = label

            labelled_pairs.loc[len(labelled_pairs)] = new_tuple

        self.pairs = labelled_pairs

    def add_labelled_pair(self, id_A, id_B, label, column_names):
        row_A = self.dataframe_A.loc[self.dataframe_A["id"] == id_A]
        row_B = self.dataframe_B.loc[self.dataframe_B["id"] == id_B]

        new_tuple = {}

        for col in column_names:
            new_tuple[col + "_A"] = row_A[col].values[0]

        for col in column_names:
            new_tuple[col + "_B"] = row_B[col].values[0]
        
        new_tuple["label"] = label

        self.pairs.loc[len(self.pairs)] = new_tuple

    def copy(self):
        return self.pairs.copy(deep=True)