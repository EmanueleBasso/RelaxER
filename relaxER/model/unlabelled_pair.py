class UnlabelledPair:
    def __init__(self, dataframe_A, dataframe_B):
        self.dataframe_A = dataframe_A
        self.dataframe_A.set_index("id", drop=False, inplace=True)

        self.dataframe_B = dataframe_B
        self.dataframe_B.set_index("id", drop=False, inplace=True)

    def remove_initial_pairs(self, initial_pair):
        for index, row in initial_pair.iterrows():
            ltable_id = row["ltable_id"]
            rtable_id = row["rtable_id"]

            self.dataframe_A = self.dataframe_A[self.dataframe_A["id"] != ltable_id]
            self.dataframe_B = self.dataframe_B[self.dataframe_B["id"] != rtable_id]

    def remove_pair(self, id_A, id_B):
        self.dataframe_A = self.dataframe_A[self.dataframe_A["id"] != id_A]
        self.dataframe_B = self.dataframe_B[self.dataframe_B["id"] != id_B]