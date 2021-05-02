from .model.labelled_pair import LabelledPair
from .model.unlabelled_pair import UnlabelledPair
from .model.similarity_function_pool import SimilarityFunctionPool

from .modules.rule_generator_module import RuleGeneratorModule
from .modules.example_selector_module import ExampleSelectorModule
from .modules.labelling_module import LabellingModule
from .modules.prediction_module import PredictionModule

from .utils import read_dataset, pick_random_tuple

class MatchingRules:
    def __init__(self, directory_path="dataset", first_table="tableA.csv", second_table="tableB.csv"):
        self.__directory_path = directory_path
        self.__dataframe_table_A = read_dataset(directory_path, first_table)
        self.__dataframe_table_B = read_dataset(directory_path, second_table)
        self.__column_names = self.__dataframe_table_A.columns

    def run_discovery(self, initial_pairs="initialPair.csv", random_start=False, number_tuple_pick=30, 
                      frac_zero_pick=25, threshold_base=0.7, min_meaningfulness=0.45, degradation=20, 
                      one_predicate_min_threshold=0.85, min_reduction_dataset=1, active_learning=True, iteration=5, 
                      number_examples_iter=10, delta=0.05, alpha=10, read_oracle=False, 
                      oracle_files=["train.csv", "test.csv", "valid.csv"], labelling_ui=False, verbose=False):
        if not isinstance(random_start, bool):
            raise ValueError("Parameter random_start must be boolean")

        if random_start:
            if number_tuple_pick < 0:
                raise ValueError("Parameter number_tuple_pick must be greater than or equal to 0")
            if (frac_zero_pick < 0) or (frac_zero_pick > 100):
                raise ValueError("Parameter frac_zero_pick must be in [0, 100]")

        if (threshold_base < 0) or (threshold_base > 1):
            raise ValueError("Parameter threshold_base must be in [0, 1]")
        if (min_meaningfulness < 0) or (min_meaningfulness > 1):
            raise ValueError("Parameter min_meaningfulness must be in [0, 1]")
        if (degradation < 0) or (degradation > 100):
            raise ValueError("Parameter degradation must be in [0, 100]")
        if (one_predicate_min_threshold < 0) or (one_predicate_min_threshold > 1):
            raise ValueError("Parameter one_predicate_min_threshold must be in [0, 1]")
        if (min_reduction_dataset < 0) or (min_reduction_dataset > 100):
            raise ValueError("Parameter min_reduction_dataset must be in [0, 100]")

        if not isinstance(active_learning, bool):
            raise ValueError("Parameter active_learning must be boolean")

        if active_learning:
            if iteration < 0:
                raise ValueError("Parameter iteration must be greater than or equal to 0")
            if number_examples_iter < 0:
                raise ValueError("Parameter number_examples_iter must be greater than or equal to 0")
            if (delta < 0) or (delta > 1):
                raise ValueError("Parameter delta must be in [0, 1]")
            if (alpha < 0) or (alpha > 100):
                raise ValueError("Parameter alpha must be in [0, 100]")
            if not isinstance(read_oracle, bool):
                raise ValueError("Parameter read_oracle must be boolean")

            if read_oracle:
                if not isinstance(oracle_files, list):
                    raise ValueError("Parameter oracle_files must be a list")
            else:
                if not isinstance(labelling_ui, bool):
                    raise ValueError("Parameter labelling_ui must be boolean")

        if not isinstance(verbose, bool):
            raise ValueError("Parameter verbose must be boolean")
        
        dataframe_initial_pairs = None

        if random_start:
            dataframe_initial_pairs = pick_random_tuple(self.__directory_path, initial_pairs, number_tuple_pick, 
                                                        frac_zero_pick)
        else:
            dataframe_initial_pairs = read_dataset(self.__directory_path, initial_pairs)

        labelled_pair = LabelledPair(self.__dataframe_table_A, self.__dataframe_table_B)
        labelled_pair.initial_labelled_pairs(dataframe_initial_pairs)

        unlabelled_pair = UnlabelledPair(self.__dataframe_table_A, self.__dataframe_table_B)
        unlabelled_pair.remove_initial_pairs(dataframe_initial_pairs)

        similarity_function_pool = SimilarityFunctionPool()

        rule_generator = RuleGeneratorModule()

        rule_repository = rule_generator.generate_rules(labelled_pair, similarity_function_pool, self.__column_names, 
                                                        one_predicate_min_threshold, min_reduction_dataset, 
                                                        threshold_base, min_meaningfulness, degradation, verbose)
        
        if active_learning:
            example_selector = ExampleSelectorModule()
            labelling = LabellingModule(read_oracle, oracle_files, self.__directory_path, labelling_ui)

            iteration_count = 0

            while iteration_count < iteration:
                if len(rule_repository) == 0:
                    break

                ### ONLY TESTING
                #print("=================> run_eval:")
                #self.run_eval(rule_repository)
                #print("")
                ###

                examples_pos, examples_neg = example_selector.select_examples(unlabelled_pair, rule_repository, 
                                                                              similarity_function_pool,
                                                                              self.__column_names, number_examples_iter, 
                                                                              threshold_base, delta, alpha, verbose)

                ### ONLY TESTING
                #with open("couples.txt", "a") as file:
                #    for example in examples_pos:
                #        file.write(str(example["id_A"]) + "," + str(example["id_B"]) + "\n")
                #    for example in examples_neg:
                #        file.write(str(example["id_A"]) + "," + str(example["id_B"]) + "\n") 
                ###

                labelling.label(examples_pos, examples_neg, labelled_pair, unlabelled_pair, self.__column_names, 
                                verbose)

                rule_repository = rule_generator.generate_rules(labelled_pair, similarity_function_pool, 
                                                                self.__column_names, one_predicate_min_threshold, 
                                                                min_reduction_dataset, threshold_base, 
                                                                min_meaningfulness, degradation, verbose)

                iteration_count = iteration_count + 1

        return rule_repository

    def run_eval(self, rule_repository, test="test.csv"):
        dataframe_test = read_dataset(self.__directory_path, test)
        similarity_function_pool = SimilarityFunctionPool()

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for index, row in dataframe_test.iterrows():
            ltable_row = self.__dataframe_table_A.loc[self.__dataframe_table_A["id"] == row["ltable_id"]]
            rtable_row = self.__dataframe_table_B.loc[self.__dataframe_table_B["id"] == row["rtable_id"]]
            label = row["label"]
            
            not_match_any_rule = True

            for rule in rule_repository:
                match = True

                for predicate in rule:
                    sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                      str(ltable_row[predicate.attribute_name].values[0]), 
                                                                      str(rtable_row[predicate.attribute_name].values[0]))

                    if sim < predicate.threshold:
                        match = False
                        break

                if match:
                    not_match_any_rule = False
                    break

            if not_match_any_rule:
                if label == 1:
                    fn = fn + 1
                else:
                    tn = tn + 1
            else:
                if label == 1:
                    tp = tp + 1
                else:
                    fp = fp + 1

        precision = 0
        if (tp + fp) != 0:
            precision = tp / (tp + fp)
        
        recall = 0
        if (tp + fn) != 0:
            recall = tp / (tp + fn)

        f_measure = 0
        if (precision + recall) != 0:
            f_measure = (2 * precision * recall) / (precision + recall)

        print("Precision: " + str(precision))
        print("Recall: " + str(recall))
        print("F-measure: " + str(f_measure))

        return precision, recall, f_measure

    def run_prediction(self, rule_repository, output="prediction.csv"):
        unlabelled_pair = UnlabelledPair(self.__dataframe_table_A, self.__dataframe_table_B)
        similarity_function_pool = SimilarityFunctionPool()

        prediction = PredictionModule()
        prediction.predict(self.__directory_path, output, rule_repository, similarity_function_pool, unlabelled_pair)