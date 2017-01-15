from src.com.FLCD.controller.controller import Controller

if __name__ == '__main__':
    ctrl = Controller()
    non_terminals, terminals, start, productions = ctrl.run()
    print("non-terminals: " + ", ".join(non_terminals))
    print("terminals: " + ", ".join(non_terminals))
    print("start: " + start)
    print(productions)
    print("productions:\n" + "{}".format(Controller.join_productions(productions)))
