from pprint import pprint

from src.com.FLCD.controller.controller import Controller

if __name__ == '__main__':
    ctrl = Controller()
    state_closure, computed_closure, goto_state, the_table = ctrl.run()
    print(state_closure)
    print(computed_closure)
    print(goto_state)
    pprint(the_table)

