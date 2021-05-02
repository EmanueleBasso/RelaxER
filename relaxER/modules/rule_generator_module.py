import pandas

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm

from ..model.rule_repository import RuleRepository
from ..model.rule import Rule
from ..model.predicate import Predicate

class RuleGeneratorModule:
    def generate_rules(self, labelled_pair, similarity_function_pool, column_names, one_predicate_min_threshold, 
                       min_reduction_dataset, threshold_base, min_meaningfulness, degradation, verbose):
        rule_repository = RuleRepository()
        
        labelled_pair_copy = labelled_pair.copy()
        labelled_pair_copy_size = len(labelled_pair_copy)
        iteration_count = 1

        while True:
            print("Iteration of generation: " + str(iteration_count))
            rule = self.__generate_one_rule(labelled_pair_copy, similarity_function_pool, column_names, threshold_base, 
                                            min_meaningfulness, degradation)

            if (rule == None) or (len(rule) == 0):
                if verbose:
                    print("\n" + "No new rule found." + "\n")
                break

            labelled_pair_copy = self.__calculate_labelled_pair(labelled_pair_copy, rule, similarity_function_pool)

            if len(labelled_pair_copy) == labelled_pair_copy_size:
                if verbose:
                    print("\n" + "No new rule found." + "\n")
                break
            else:
                labelled_pair_copy_size = len(labelled_pair_copy)

            rule_repository.append(rule)

            if verbose:
                precision, recall, f_measure = self.__calculate_precision_recall_f_measure(labelled_pair.pairs, 
                                                                                           rule_repository, 
                                                                                           similarity_function_pool)

                print("\n" + "Precision: " + str(precision))
                print("Recall: " + str(recall))
                print("F-measure: " + str(f_measure))
                print("Size labelled pairs remaining: " + str(labelled_pair_copy_size))
                print("\n" + str(rule_repository))

            if len(labelled_pair_copy) <= ((min_reduction_dataset * len(labelled_pair.pairs)) / 100):
                break

            iteration_count = iteration_count + 1

        print("Removing unecessary rules...")

        self.__check_rule_one_predicate(rule_repository, one_predicate_min_threshold)
        self.__check_contained_rule(rule_repository)

        print("Done.")
        if verbose:
            print("\n" + str(rule_repository))

        return rule_repository

    def __generate_one_rule(self, labelled_pair, similarity_function_pool, column_names, threshold_base, 
                            min_meaningfulness, degradation):
        rule = Rule()

        tot_len = ((len(column_names) - 1) * len(similarity_function_pool)) + ((len(column_names) - 1) * int((1 - threshold_base) * 100))
        bar = tqdm(total=tot_len)

        for col_name in column_names:
            if col_name == "id":
                continue
        
            meaningfulness_best = -1
            precision_best = -1
            recall_best = -1
            f_id_best = -1
            for i in range(len(similarity_function_pool)):
                predicate = Predicate(col_name, i, threshold_base)
                rule.append(predicate)

                precision, recall, meaningfulness = self.__calculate_precision_recall_meaningfulness(labelled_pair, 
                                                                                                    rule, 
                                                                                                    similarity_function_pool)

                if (meaningfulness >= min_meaningfulness) and (meaningfulness >= meaningfulness_best) and (precision >= precision_best) and (recall >= recall_best):
                    meaningfulness_best = meaningfulness
                    precision_best = precision
                    recall_best = recall
                    f_id_best = i

                del rule[col_name]
                bar.update(1)

            if f_id_best != -1:
                rule.append(Predicate(col_name, f_id_best, threshold_base))

        directions = {}
        for predicate in rule:
                directions[predicate.attribute_name] = "up"

        precision, recall_originary = self.__calculate_precision_recall(labelled_pair, rule, similarity_function_pool)

        step = 0.01
        while True:
            for predicate in rule:
                if directions[predicate.attribute_name] == "stable":
                    continue
                if predicate.threshold > 1.0:
                    directions[predicate.attribute_name] = "stable"
                    continue

                predicate.threshold += step

                precision_2, recall_2 = self.__calculate_precision_recall(labelled_pair, rule, similarity_function_pool)
            
                degradation_calc = 0
                if recall_originary != 0:
                    degradation_calc = (recall_originary - recall_2) * 100 / recall_originary

                if (precision_2 < precision) or (degradation_calc > degradation):
                    predicate.threshold -= step
                    directions[predicate.attribute_name] = "stable"
                    bar.update(int(((1.0 - predicate.threshold) * 100)))
                else:
                    precision = precision_2
                    bar.update(1)
            
            finish = True
            for val in directions.values():
                if val == "up":
                    finish = False
                    break

            if finish:
                break

        bar.n = tot_len
        bar.refresh()
        bar.close()
        
        return rule

    def __calculate_precision_recall(self, labelled_pair, rule, similarity_function_pool):
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for index, row in labelled_pair.iterrows():
            match = True

            for predicate in rule:
                sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                  str(row[predicate.attribute_name + "_A"]), 
                                                                  str(row[predicate.attribute_name + "_B"]))

                if sim < predicate.threshold:
                    match = False
                    break
            
            if match:
                if row["label"] == 1:
                    tp = tp + 1
                else:
                    fp = fp + 1
            else:
                if row["label"] == 1:
                    fn = fn + 1
                else:
                    tn = tn + 1

        precision = 0
        if (tp + fp) != 0:
            precision = tp / (tp + fp)
        
        recall = 0
        if (tp + fn) != 0:
            recall = tp / (tp + fn)

        return precision, recall

    def __calculate_precision_recall_meaningfulness(self, labelled_pair, rule, similarity_function_pool):
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        count_t = 0
        tot = 0

        for index, row in labelled_pair.iterrows():
            match = True

            for predicate in rule:
                sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                  str(row[predicate.attribute_name + "_A"]), 
                                                                  str(row[predicate.attribute_name + "_B"]))

                if sim < predicate.threshold:
                    match = False
                    break
            
            if match:
                if row["label"] == 1:
                    tp = tp + 1
                    count_t = count_t + 1
                else:
                    fp = fp + 1
            else:
                if row["label"] == 1:
                    fn = fn + 1
                else:
                    tn = tn + 1
                    count_t = count_t + 1

            tot = tot + 1

        precision = 0
        if (tp + fp) != 0:
            precision = tp / (tp + fp)
        
        recall = 0
        if (tp + fn) != 0:
            recall = tp / (tp + fn)

        meaningfulness = 0
        if tot != 0:
            meaningfulness = count_t / tot

        return precision, recall, meaningfulness

    def __calculate_labelled_pair(self, labelled_pair, rule, similarity_function_pool):
        labelled_pair_copy = pandas.DataFrame(columns=labelled_pair.columns)

        for index, row in labelled_pair.iterrows():
            match = True

            for predicate in rule:
                sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                  str(row[predicate.attribute_name + "_A"]), 
                                                                  str(row[predicate.attribute_name + "_B"]))

                if sim < predicate.threshold:
                    match = False
                    break
            
            if match:
                if row["label"] == 0:
                    labelled_pair_copy.loc[len(labelled_pair_copy)] = row
            else:
                if row["label"] == 1:
                    labelled_pair_copy.loc[len(labelled_pair_copy)] = row

        return labelled_pair_copy

    def __calculate_precision_recall_f_measure(self, labelled_pair, rule_repository, similarity_function_pool):
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for index, row in labelled_pair.iterrows():            
            not_match_any_rule = True

            for rule in rule_repository:
                match = True

                for predicate in rule:
                    sim = similarity_function_pool.compute_similarity(predicate.function_id, 
                                                                      str(row[predicate.attribute_name + "_A"]), 
                                                                      str(row[predicate.attribute_name + "_B"]))

                    if sim < predicate.threshold:
                        match = False
                        break

                if match:
                    not_match_any_rule = False
                    break

            if not_match_any_rule:
                if row["label"] == 1:
                    fn = fn + 1
                else:
                    tn = tn + 1
            else:
                if row["label"] == 1:
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
        
        return precision, recall, f_measure

    def __check_rule_one_predicate(self, rule_repository, one_predicate_min_threshold):
        rules_to_remove = []

        for i in range(len(rule_repository)):
            rule = rule_repository[i]

            if (len(rule) == 1) and (rule.predicates[0].threshold < one_predicate_min_threshold):
                rules_to_remove.append(i)

        rules_to_remove.reverse()

        for i in rules_to_remove:
            del rule_repository[i]

    def __check_contained_rule(self, rule_repository):
        def __is_contained_rule(rule_1, rule_2):
            if len(rule_1) != len(rule_2):
                return False

            for predicate_2 in rule_2:
                predicate_1 = rule_1[predicate_2.attribute_name]

                if predicate_1 is None:
                    return False

                if predicate_1.function_id != predicate_2.function_id:
                    return False
                    
                if predicate_1.threshold > predicate_2.threshold:
                    return False

            return True

        rules_to_remove = []

        for i in range(len(rule_repository)):
            rule_1 = rule_repository[i]

            if i in rules_to_remove:
                continue
            else:
                for j in range(len(rule_repository)):
                    if i == j:
                        continue
                    if j in rules_to_remove:
                        continue
                    else:
                        rule_2 = rule_repository[j]

                        if __is_contained_rule(rule_1, rule_2):
                            rules_to_remove.append(j)

        rules_to_remove = list(dict.fromkeys(rules_to_remove))
        rules_to_remove.reverse()

        for k in rules_to_remove:
            del rule_repository[k]