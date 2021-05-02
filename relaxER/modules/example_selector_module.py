import itertools

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm

from ..model.rule_repository import RuleRepository
from ..model.rule import Rule
from ..model.predicate import Predicate

class ExampleSelectorModule:
    def __init__(self):
        self.__start_position = 0

    def select_examples(self, unlabelled_pair, rule_repository, similarity_function_pool, column_names, 
                        number_examples_to_pick, threshold_base, delta, alpha, verbose):
        rule_repository_relaxed = self.__relax_rules(rule_repository, threshold_base, alpha, verbose)

        number_examples_selected_pos = 0
        number_examples_selected_neg = 0
        list_picked_dataframe_B = []

        examples_pos = []
        examples_neg = []

        print("Examples selection:")

        tot_len = len(unlabelled_pair.dataframe_A) * len(unlabelled_pair.dataframe_B)
        bar = tqdm(total=tot_len)
        
        for index_A, row_A in self.__get_iterable(unlabelled_pair.dataframe_A):
            self.__start_position = (self.__start_position + 1) % len(unlabelled_pair.dataframe_A)
            skip = False

            for index_B, row_B in unlabelled_pair.dataframe_B.iterrows(): 
                if row_B["id"] in list_picked_dataframe_B:
                    bar.update(1)
                    continue
                
                delta_calc = 0

                for rule in rule_repository:
                    match = True
                    sum = 0

                    for predicate in rule:
                        sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                          str(row_A[predicate.attribute_name]), 
                                                                          str(row_B[predicate.attribute_name]))

                        if sim < predicate.threshold:
                            match = False
                            break
                        else:
                            sum = sum + (sim - predicate.threshold)

                    if match:
                        delta_calc = sum / len(rule)
                        break

                if delta_calc > 0:
                    if number_examples_selected_pos < number_examples_to_pick:
                        if delta_calc < delta:
                            examples_pos.append({
                                "id_A": row_A["id"],
                                "id_B": row_B["id"]
                            })

                            number_examples_selected_pos += 1
                            skip = True
                            list_picked_dataframe_B.append(row_B["id"])
                else:
                    if number_examples_selected_neg < number_examples_to_pick:
                        not_match_any_rule = True

                        for rule in rule_repository_relaxed:
                            match = True

                            for predicate in rule:
                                sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                                  str(row_A[predicate.attribute_name]), 
                                                                                  str(row_B[predicate.attribute_name]))

                                if sim < predicate.threshold:
                                    match = False
                                    break

                            if match:
                                not_match_any_rule = False
                                break

                        if not not_match_any_rule:
                            examples_neg.append({
                                "id_A": row_A["id"],
                                "id_B": row_B["id"]
                            })

                            number_examples_selected_neg += 1
                            skip = True
                            list_picked_dataframe_B.append(row_B["id"])

                if (number_examples_selected_pos + number_examples_selected_neg) == (2 * number_examples_to_pick):
                    bar.n = tot_len
                    bar.refresh()
                    bar.close()
                    return examples_pos, examples_neg

                bar.update(1)

                if skip:
                    bar.update(len(unlabelled_pair.dataframe_B) - index_B - 1)
                    break

        bar.n = tot_len
        bar.refresh()
        bar.close()
        return examples_pos, examples_neg

    def __relax_rules(self, rule_repository, threshold_base, alpha, verbose):
        rule_repository_relaxed = RuleRepository()

        for rule in rule_repository:
            rule_relaxed = Rule()

            for predicate in rule:
                t = predicate.threshold - ((alpha * predicate.threshold) / 100)

                if t >= threshold_base:
                    predicate_relaxed = Predicate(predicate.attribute_name, predicate.function_id, t)
                    rule_relaxed.append(predicate_relaxed)
            
            if len(rule_relaxed) != 0:
                rule_repository_relaxed.append(rule_relaxed)

        if verbose:
            print("Rule Repository after relaxation:")            
            print(rule_repository_relaxed)

        return rule_repository_relaxed

    def __get_iterable(self, dataframe):
        if self.__start_position > 0:
            first_iter = itertools.islice(dataframe.iterrows(), self.__start_position, None)
            second_iter = itertools.islice(dataframe.iterrows(), 0, self.__start_position - 1)

            return itertools.chain(first_iter, second_iter)
        else:
            return dataframe.iterrows()