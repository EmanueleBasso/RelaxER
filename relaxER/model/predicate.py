from .similarity_function_pool import SimilarityFunctionPool

class Predicate:
    def __init__(self, attribute_name, function_id, threshold):
        self.attribute_name = attribute_name
        self.function_id = function_id
        self.threshold = threshold

    def __str__(self):
        return SimilarityFunctionPool.Function_printable_name[self.function_id] +  "(" + self.attribute_name + ", " + str(round(self.threshold, 2)) + ")"