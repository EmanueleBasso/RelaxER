import py_stringmatching as sm

class SimilarityFunctionPool:
    BAG_DISTANCE = 0
    COSINE = 1
    DICE = 2
    EDITEX = 3
    GENERALIZED_JACCARD = 4
    JACCARD = 5
    JARO = 6
    JARO_WINKLER = 7
    LEVENSHTEIN = 8
    OVERLAP_COEFFICIENT = 9
    TVERSKY_INDEX = 10

    Function_printable_name = [
        "Bag-Distance",
        "Cosine",
        "Dice",
        "Editex",
        "Generalized-Jaccard",
        "Jaccard",
        "Jaro",
        "Jaro-Winkler",
        "Levenshtein",
        "Overlap-Coefficient",
        "Tversky-Index"
    ]

    def __init__(self):
        self.similarity_function = [
            sm.BagDistance(),
            sm.Cosine(),
            sm.Dice(),
            sm.Editex(),
            sm.GeneralizedJaccard(),
            sm.Jaccard(),
            sm.Jaro(),
            sm.JaroWinkler(),
            sm.Levenshtein(),
            sm.OverlapCoefficient(),
            sm.TverskyIndex()
        ]

        self.alphanumeric_tokenizer = sm.AlphanumericTokenizer(return_set=True)

    def __len__(self):
        return len(self.similarity_function)

    def compute_similarity(self, function_id, string_A, string_B):
        string_A_elaborated = string_A
        string_B_elaborated = string_B

        if string_A_elaborated == "nan":
            string_A_elaborated = ""
        
        if string_B_elaborated == "nan":
            string_B_elaborated = ""

        if function_id == self.COSINE or function_id == self.DICE or function_id == self.GENERALIZED_JACCARD or function_id == self.JACCARD or function_id == self.OVERLAP_COEFFICIENT or function_id == self.TVERSKY_INDEX:
            string_A_elaborated = self.alphanumeric_tokenizer.tokenize(string_A_elaborated)
            string_B_elaborated = self.alphanumeric_tokenizer.tokenize(string_B_elaborated)

        return self.similarity_function[function_id].get_sim_score(string_A_elaborated, string_B_elaborated)