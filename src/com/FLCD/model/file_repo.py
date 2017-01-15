from collections import defaultdict


class FileRepo(object):
    @classmethod
    def read_from_file(cls, filename):
        with open(filename, 'r') as f:
            non_terminals = cls.process_nodes(f.readline())
            terminals = cls.process_nodes(f.readline())
            start = f.readline().split(" = ")[1].rstrip("\n")
            productions = cls.process_productions(f.readlines())
        return non_terminals, terminals, start, productions

    @classmethod
    def process_nodes(cls, string):
        nodes_string = string.split(" = ")[1].rstrip("\n")
        nodes = nodes_string.split(", ")
        return nodes

    @classmethod
    def process_productions(cls, string_arr):
        productions_string = [el.rstrip("\n").split(" -> ") for el in string_arr]
        productions = defaultdict(list)
        for productions_list in productions_string:
            productions[productions_list[0]].append([el.strip() for el in productions_list[1].split(" | ")])
        return productions
