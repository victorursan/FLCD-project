import re

from src.com.FLCD.model.file_repo import FileRepo


class Controller(object):
    def __init__(self):
        self.__non_terminals, self.__terminals, self.__start, self.__productions = FileRepo.read_from_file("grammar")
        self.__state_closure = []
        self.__computed_closure = []
        self.__goto_state = {}

    def run(self):
        self.__productions = self.find_productions()

        start_point = [(self.__start, self.add_dot(self.__productions[self.__start][0]))]
        self.__state_closure.append(start_point)
        self.__computed_closure.append(self.compute_closure(start_point))

        self.canonical_collection_of_states()

        return self.__state_closure, self.__computed_closure, self.__goto_state

    def canonical_collection_of_states(self, poz=0):
        to_do = set(
            map(lambda y: self.get_next(y[1]),
                filter(lambda x: not self.is_finished(x[1]), self.__computed_closure[poz])))
        for t in to_do:
            clj = self.goto_to_closure(poz, t)
            if clj not in self.__state_closure:
                self.__state_closure.append(clj)
                self.__computed_closure.append(self.compute_closure(clj))
            self.__goto_state[(poz, t)] = self.__state_closure.index(clj)
        if poz != max(self.__goto_state.values()):
            self.canonical_collection_of_states(poz + 1)

    def find_productions(self):
        new_productions = {}
        to_split = self.__non_terminals + self.__terminals
        for k, v in self.__productions.items():
            new_val = []
            for val in v:
                pattern = "(" + "|".join(map(lambda x: re.escape(x), to_split)) + ")"
                n_v = filter(lambda x: x, re.split(pattern, val[0]))
                new_val.append(n_v)
            new_productions[k] = new_val
        return new_productions

    @staticmethod
    def add_dot(lst):
        return ["."] + lst

    @staticmethod
    def move(lst):
        ind = lst.index(".")
        new_list = lst[:]
        new_list[ind], new_list[ind + 1] = new_list[ind + 1], new_list[ind]
        return new_list

    @staticmethod
    def is_finished(lst):
        return lst[-1] == "."

    @staticmethod
    def get_next(lst):
        return lst[lst.index(".") + 1]

    def compute_closure(self, lst):
        new_lst = lst[:]
        for tupl in lst:
            if not self.is_finished(tupl[1]):
                ne = self.get_next(tupl[1])
                # poz = self.__state_closure.index(tupl)
                if ne in self.__productions.keys():
                    new_lst.extend(
                        filter(lambda y: y not in new_lst,
                               map(lambda x: (ne, self.add_dot(x)), self.__productions[ne])))
        if len(new_lst) != len(lst):
            return self.compute_closure(new_lst)
        return new_lst

    def goto_to_closure(self, state, itm):
        return list(map(lambda y: (y[0], self.move(y[1])), filter(lambda x: not self.is_finished(x[1])
                                                                            and self.get_next(x[1]) == itm,
                                                                  self.__computed_closure[state])))

    @staticmethod
    def join_productions(productions):
        return [k + " -> " + " | ".join([",".join(e) for e in v]) for k, v in productions.items()]
