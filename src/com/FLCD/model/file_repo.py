import re

from collections import defaultdict


class FileRepo(object):
    @classmethod
    def read_from_file(cls, filename):
        with open(filename, 'r') as f:
            non_terminals = cls.process_nodes(f.readline())
            terminals = cls.process_nodes(f.readline())
            start = f.readline().split(" -> ")[1].rstrip("\n")
            productions = cls.process_productions(f.readlines())
        return non_terminals, terminals, start, productions

    @classmethod
    def process_nodes(cls, string):
        nodes_string = string.split(" -> ")[1].rstrip("\n")
        nodes = nodes_string.split(" ")
        return nodes

    @classmethod
    def process_productions(cls, string_arr):
        productions_string = [el.rstrip("\n").split(" -> ") for el in string_arr]
        productions = defaultdict(list)
        for productions_list in productions_string:
            productions[productions_list[0]].append([el.strip() for el in productions_list[1].split(" | ")])
        return productions

    @classmethod
    def process_input(cls, filename, terminals):
        input_prog = []
        with open(filename, 'r') as f:
            pattern = "(" + "|".join(map(lambda x: re.escape(x), terminals)) + ")"
            for line in f.readlines():
                n_v = filter(lambda x: x.strip(), re.split(pattern,line))
                input_prog.extend(n_v)
        return input_prog

    @classmethod
    def process_input2(cls, filename, pif):
        input_prog = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                int_value = int(line)
                input_prog.append(pif[int_value])
        return input_prog

    @classmethod
    def read_pif(cls, filename):
        input_prog = {}
        with open(filename, 'r') as f:
            for line in f.readlines():
                pair = line.split(" ")
                pif_code = int(pair[1])
                input_prog[pif_code] = pair[0]
        return input_prog