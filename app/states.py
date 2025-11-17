from aiogram.fsm.state import State, StatesGroup


class Send_message(StatesGroup):
    receive_message = State()


class Answer_message(StatesGroup):
    receive_answer_message = State()


class Find_out_who(StatesGroup):
    Check_status = State()
