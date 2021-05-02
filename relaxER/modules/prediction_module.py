import pandas
import os

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm

class PredictionModule:
    def predict(self, directory_path, file_output_name, rule_repository, similarity_function_pool, unlabelled_pair):
        columns_name = []
        columns_name.append("ltable_id")
        columns_name.append("rtable_id")
        columns_name.append("label")

        match_pairs = pandas.DataFrame(columns=columns_name)

        list_picked_dataframe_B = []

        print("Prediction:")

        tot_len = len(unlabelled_pair.dataframe_A) * len(unlabelled_pair.dataframe_B)
        bar = tqdm(total=tot_len)

        for index_A, row_A in unlabelled_pair.dataframe_A.iterrows():
            skip = False

            for index_B, row_B in unlabelled_pair.dataframe_B.iterrows(): 
                if row_B["id"] in list_picked_dataframe_B:
                    bar.update(1)
                    continue

                not_match_any_rule = True

                for rule in rule_repository:
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
                    new_tuple = {}
                    new_tuple["ltable_id"] = row_A["id"]
                    new_tuple["rtable_id"] = row_B["id"]
                    new_tuple["label"] = "1"

                    match_pairs.loc[len(match_pairs)] = new_tuple

                    skip = True
                    list_picked_dataframe_B.append(row_B["id"])

                bar.update(1)

                if skip:
                    bar.update(len(unlabelled_pair.dataframe_B) - index_B - 1)
                    break

        bar.n = tot_len
        bar.refresh()
        bar.close()

        print("Creating output file...")
        match_pairs.to_csv(os.path.join(directory_path, file_output_name), index=False, encoding="utf-8")
        print("Done.")