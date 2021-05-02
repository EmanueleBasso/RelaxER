import pickle

class RuleRepository:
    def __init__(self):
        self.rules = []

    def append(self, rule):
        self.rules.append(rule)

    def __len__(self):
        return len(self.rules)

    def __delitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Index must be a number")
        if index > (len(self.rules) - 1):
            raise KeyError("Out of bound index")
        else:
            del self.rules[index]

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Index must be a number")
        if index > (len(self.rules) - 1):
            raise KeyError("Out of bound index")
        else:
            return self.rules[index]

    def __iter__(self):
        self.__iteration_index = 0
        return self

    def __next__(self):
        if self.__iteration_index < self.__len__():
            o = self.rules[self.__iteration_index]
            self.__iteration_index += 1
            return o
        else:
            raise StopIteration

    def __str__(self):
        s = "Rule Repository:\n"

        for rule in self.rules:
            s += "\t" + str(rule) + "\n"

        return s

    def show_rules(self):
        print(self.__str__())

    @staticmethod
    def import_rules(input_file_name="rule_repository.pickle"):
        infile = None

        try:
            infile = open(input_file_name, "rb")

            rule_repository = pickle.load(infile)

            return rule_repository
        except:
            print("File cannot be read!")
            return None
        finally:
            infile.close()

    def export_rules(self, output_file_name="rule_repository.pickle"):
        outfile = None

        try:
            outfile = open(output_file_name, "wb")

            pickle.dump(self, outfile)

            return 0
        except:
            print("File cannot be written!")
            return None
        finally:
            outfile.close()