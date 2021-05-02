from ..core import MatchingRules

from .user_interrupt_labelling_exception import UserInterruptLabellingException

def run_discovery(queue, event, directory_path, first_table, second_table, initial_pair, active_learning, 
                  threshold_base, min_meaningfulness, degradation, one_predicate_min_threshold, min_reduction_dataset, 
                  iteration, number_examples_iter, delta, alpha, random_start, number_tuple_pick, frac_zero_pick, 
                  read_oracle, oracle_files):
    try:
        matching_rules = MatchingRules(directory_path, first_table, second_table)

        rule_repository = matching_rules.run_discovery(initial_pair,
                                                       random_start,
                                                       number_tuple_pick,
                                                       frac_zero_pick,
                                                       threshold_base,
                                                       min_meaningfulness,
                                                       degradation,
                                                       one_predicate_min_threshold,
                                                       min_reduction_dataset,
                                                       active_learning,
                                                       iteration,
                                                       number_examples_iter,
                                                       delta,
                                                       alpha,
                                                       read_oracle,
                                                       "".join(oracle_files.split()).split(","),
                                                       True,
                                                       True
                                                    )

        queue.put(rule_repository)
        event.set()
    except UserInterruptLabellingException:
        queue.put("Stopped")
        event.set()
    except KeyboardInterrupt:
        pass
    except Exception as exception:
        queue.put(exception)
        event.set()

def run_eval(queue, event, rule_repository, directory_path, first_table, second_table, test):
    try:
        matching_rules = MatchingRules(directory_path, first_table, second_table)

        precision, recall, fmeasure = matching_rules.run_eval(rule_repository, test)
        
        queue.put(precision)
        queue.put(recall)
        queue.put(fmeasure)
        event.set()
    except KeyboardInterrupt:
        pass
    except Exception as exception:
        queue.put(exception)
        event.set()

def run_prediction(queue, event, rule_repository, directory_path, first_table, second_table, output):
    try:
        matching_rules = MatchingRules(directory_path, first_table, second_table)

        matching_rules.run_prediction(rule_repository, output)

        queue.put("Finished")
        event.set()
    except KeyboardInterrupt:
        pass
    except Exception as exception:
        queue.put(exception)
        event.set()