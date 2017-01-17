import re
from collections import OrderedDict
from collections import defaultdict
from pprint import pprint

from src.com.FLCD.model.file_repo import FileRepo


class Controller(object):
    def __init__(self):
        self.__non_terminals, self.__terminals, self.__start, self.__productions = FileRepo.read_from_file("grammar2")
        self.__state_closure = []
        self.__computed_closure = []
        self.__goto_state = {}
        self.__the_table = {}
        self.__ordered_productions = []
        self.__follow = defaultdict(list)
        self.__workstack = []
        self.__input = []
        self.__output = []

    def run(self):
        self.__productions = self.find_productions()
        for k, v in self.__productions.items():
            for value in v:
                self.__ordered_productions.append((k, value))
        # print(self.join_productions(self.__productions))
        start_point = [(self.__start, self.add_dot(self.__productions[self.__start][0]))]
        self.__state_closure.append(start_point)
        self.__computed_closure.append(self.compute_closure(start_point))

        self.canonical_collection_of_states()
        self.__follow = self.follow()
        # print(self.follow())

        for i in range(max(self.__goto_state.values()) + 1):
            for j in ["#"] + self.__non_terminals + self.__terminals:
                if (i, j) not in self.__the_table.keys():
                    self.__the_table[(i, j)] = self.get_shift(i, j)
                if self.has_final(self.get_shift(i, j)):
                    finals = self.get_finals(self.get_shift(i, j))
                    for final in finals:
                        if self.is_accept(final):
                            self.__the_table[(self.get_shift(i, j), '$')] = "acc"
                        else:
                            for f in self.__follow[final[0]]:
                                r_final = (final[0], final[1][:-1])
                                self.__the_table[(self.get_shift(i, j), f if f != '#' else '$')] = "R" + str(self.__ordered_productions.index(r_final))

        self.process_input()
        print(self.__workstack)
        print(self.__input)
        print(self.__output)
        for i in range (len(self.__ordered_productions)):
            print(str(i) + " :" + str(self.__ordered_productions[i]))
        to_repl = self.process_result()
        print(to_repl)

        return self.__state_closure, self.__computed_closure, self.__goto_state, self.__the_table, self.__terminals

    def get_shift(self, i, j):
        return self.__goto_state[(i, j)] if (i, j) in self.__goto_state.keys() else "#"

    def canonical_collection_of_states(self, poz=0):
        to_do = []
        for e in map(lambda y: self.get_next(y[1]),
                     filter(lambda x: not self.is_finished(x[1]), self.__computed_closure[poz])):
            if e not in to_do:
                to_do.append(e)

        for t in to_do:
            clj = self.goto_to_closure(poz, t)
            if clj not in self.__state_closure:
                self.__state_closure.append(clj)
                self.__computed_closure.append(self.compute_closure(clj))
            self.__goto_state[(poz, t)] = self.__state_closure.index(clj)
        if poz != max(self.__goto_state.values()):
            self.canonical_collection_of_states(poz + 1)

    def find_productions(self):
        new_productions = OrderedDict()
        to_split = self.__non_terminals + self.__terminals
        for k, v in self.__productions.items():
            new_val = []
            for val in v:
                pattern = "(" + "|".join(map(lambda x: re.escape(x), to_split)) + ")"
                n_v = map(lambda y: y.strip(), filter(lambda x: len(x.strip()) > 0, re.split(pattern, val[0])))
                new_val.append(n_v)
            new_productions[k] = new_val
        return new_productions

    def has_final(self, prod):
        if isinstance(prod, int):
            return any([self.is_finished(x[1]) for x in self.__computed_closure[prod]])
        return False

    def get_finals(self, prod):
        return filter(lambda x: self.is_finished(x[1]), self.__computed_closure[prod])

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
        return [k + " -> " + " | ".join(["".join(e) for e in v]) for k, v in productions.items()]

    def is_accept(self, pr):
        return pr[0] == self.__start and self.is_finished(pr[1])

    def first(self):
        first_map = {"#": set("#")}

        for terminal in self.__terminals:
            first_map[terminal] = {terminal}

        for non_terminal in self.__non_terminals:
            values = set()
            for prod in self.__productions[non_terminal]:
                first = prod[0]
                if first in self.__terminals or first == "#":
                    values.add(first)
            first_map[non_terminal] = values

        changed = True
        while changed:
            changed = False
            for non_terminal in self.__non_terminals:
                for rhs in self.__productions[non_terminal]:
                    if all([len(first_map[e]) > 0 for e in rhs]):
                        vals = set()
                        for token in rhs:
                            vals |= first_map[token]
                            if "#" not in first_map[token]:
                                if "#" in vals:
                                    vals.remove("#")
                                break
                        if not vals.issubset(first_map[non_terminal]):
                            first_map[non_terminal] |= vals
                            changed = True

        return first_map

    @staticmethod
    def first_sq(firsts, sq):
        result = {"#"}
        for token in sq:
            result |= firsts[token]
            if "#" not in firsts[token]:
                if "#" in result:
                    result.remove("#")
                break
        return result

    def follow(self):
        first_map = self.first()
        follow_map = defaultdict(set)
        follow_map[self.__start] = {"#"}
        changed = True
        while changed:
            changed = False
            for non_terminal in self.__non_terminals:
                for k, v in self.__productions.items():
                    for rhs in v:
                        if non_terminal in rhs:
                            sub_sq = rhs[rhs.index(non_terminal) + 1:]
                            first_sq = self.first_sq(first_map, sub_sq)
                            first_sq_noeps = filter(lambda x: x != "#", first_sq)

                            if not set(first_sq_noeps).issubset(follow_map[non_terminal]):
                                follow_map[non_terminal] |= set(first_sq_noeps)
                                changed = True
                            if "#" in first_sq:
                                if not set(follow_map[k]).issubset(follow_map[non_terminal]):
                                    follow_map[non_terminal] |= follow_map[k]
                                    changed = True
        return follow_map

    def process_input(self):
        pif = FileRepo.read_pif("pif.txt")
        self.__input = FileRepo.process_input2("inputScanner", pif)
        # self.__input = FileRepo.process_input("input", self.__terminals)
        self.__input.append('$')
        self.__workstack.append(0)
        self.__output.append("#")
        pprint(self.__the_table)

        while True:
            crt = self.__input[0]
            el = self.__workstack[-1]
            if self.is_acc(crt, el) and len(self.__input) == 1:
                self.__workstack = ['$', 'acc']
                break
            elif self.to_shift(crt, el):
                act = self.get_shift_value(crt, el)
                if not crt == "$":
                    self.__input.pop(0)
                else:
                    print("Smth when wrong")
                    break
                self.__workstack.append(crt)
                self.__workstack.append(act)
            else:
                act = self.get_reduce(crt, el)
                if act != '#':
                    k, v = self.get_production(act)
                    much = len(v) * 2
                    self.__workstack = self.__workstack[:-much]
                    self.add_to_output(act)
                    prv = self.__workstack[-1]
                    self.__workstack.append(k)
                    self.__workstack.append(self.__the_table[(prv, k)])

                else:
                    prv = self.__workstack[-1]
                    self.__workstack.append('#')
                    self.__workstack.append(self.__the_table[(prv, '#')])

    def to_shift(self, crt, el):
        return isinstance(self.__the_table[(el, crt)], int)

    def get_shift_value(self, crt, el):
        return self.__the_table[(el, crt)]

    def get_reduce(self, crt, el):
        result = self.__the_table[(el, crt)]
        if result != '#':
            return int(result.replace("R", ""))
        return '#'

    def get_production(self, i):
        return self.__ordered_productions[i]

    def add_to_output(self, act):
        if self.__output[0] == "#":
            self.__output[0] = act
        else:
            self.__output.insert(0, act)

    def is_acc(self, crt, el):
        return self.__the_table[(el, crt)] == "acc"

    def process_result(self):
        prods = []
        for i in self.__output:
            prods.append(self.get_production(i))
        to_replace = prods[0]
        prods = prods[1:]
        for prod in prods:
            print(to_replace)
            if prod[0] in to_replace[1]:
                idxs = [pos for pos, itm in enumerate(to_replace[1]) if itm == prod[0]]
                idx = idxs[-1]
                to_replace[1][idx:idx + 1] = prod[1]
        return to_replace
