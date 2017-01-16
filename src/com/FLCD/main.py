from pprint import pprint

from src.com.FLCD.controller.controller import Controller
from src.com.FLCD.model.file_repo import FileRepo

if __name__ == '__main__':
    ctrl = Controller()
    state_closure, computed_closure, goto_state, the_table, terms = ctrl.run()
    # print(state_closure)
    # print(computed_closure)
    # print(goto_state)
    # pprint(the_table)
    #

