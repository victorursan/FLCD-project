from src.com.FLCD.model.file_repo import FileRepo


class Controller(object):
    def __init__(self):
        self.__non_terminals, self.__terminals, self.__start, self.__productions = FileRepo.read_from_file("grammar")

    def run(self):
        productive = self.find_productive([])
        productions = self.get_productive_productions(productive)
        return productive, self.__terminals, self.__start, productions

    def find_productive(self, productive=None):
        if productive is None:
            productive = []
        new_productive = productive
        for k, v in self.__productions.items():
            if self.is_productive(v, productive) and k not in productive:
                new_productive.append(k)
        if new_productive == productive:
            return productive
        return self.find_productive(new_productive)

    def is_productive(self, productions, productive):
        return any(self.is_prod(el, productive) or el == "&" for el in productions)

    def is_prod(self, el, productive):
        return all(e in productive or e in self.__terminals for e in list(el))

    def get_unproductive(self, productive):
        return [e for e in self.__non_terminals if e not in productive]

    def get_productive_productions(self, productive):
        new_productions = {}
        # print(self.__productions.items())
        for k, v in self.__productions.items():
            if k in productive:
                prod = [e for e in v if self.is_prod(e, productive)]
                if prod:
                    new_productions[k] = prod
        return new_productions

    @staticmethod
    def join_productions(productions):
        print(productions.items())
        return [k + " -> " + " | {}".format(v) for k, v in productions.items()] #todo ...fix this
