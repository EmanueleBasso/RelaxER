class Rule:
    def __init__(self):
        self.predicates = []

    def append(self, predicate):
        self.predicates.append(predicate)

    def __len__(self):
        return len(self.predicates)

    def __delitem__(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        else:
            for predicate in self.predicates:
                if predicate.attribute_name == name:
                    self.predicates.remove(predicate)
                    return
            
            raise KeyError("Predicate not present")

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        else: 
            for predicate in self.predicates:
                if predicate.attribute_name == name:
                    return predicate
            
            return None

    def __iter__(self):
        self.__iteration_index = 0
        return self

    def __next__(self):
        if self.__iteration_index < self.__len__():
            o = self.predicates[self.__iteration_index]
            self.__iteration_index += 1
            return o
        else:
            raise StopIteration

    def __str__(self):
        s = "Rule: "
        
        for predicate in self.predicates:
            if len(s) != 6:
                s += " and "
            s += str(predicate)

        return s