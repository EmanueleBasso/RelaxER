import os
import pandas

def read_dataset(directory_path, table_name):
    return pandas.read_csv(os.path.join(directory_path, table_name), encoding="utf-8")

def pick_random_tuple(directory_path, table_name, tot, frac_zero):
    dataframe = read_dataset(directory_path, table_name)
    
    dataframe_sample_0 = dataframe[dataframe["label"] == 0]
    dataframe_sample_1 = dataframe[dataframe["label"] == 1]

    num_sample_0 = int((frac_zero * tot) / 100)
    num_sample_1 = tot - num_sample_0

    if (len(dataframe_sample_0) >= num_sample_0) and (len(dataframe_sample_1) >= num_sample_1):
        dataframe_sample_0 = dataframe_sample_0.sample(n=num_sample_0)
        dataframe_sample_1 = dataframe_sample_1.sample(n=num_sample_1)
    elif (len(dataframe_sample_0) >= num_sample_0) and (len(dataframe_sample_1) < num_sample_1):
        dataframe_sample_0 = dataframe_sample_0.sample(n=(tot - len(dataframe_sample_1)))
    elif (len(dataframe_sample_0) < num_sample_0) and (len(dataframe_sample_1) >= num_sample_1):
        dataframe_sample_1 = dataframe_sample_1.sample(n=(tot - len(dataframe_sample_0)))
    else:
        pass

    dataframe_sample = pandas.concat([dataframe_sample_0, dataframe_sample_1]).sample(frac=1)

    return dataframe_sample